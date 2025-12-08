from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountReconcileWizard(models.TransientModel):
    _inherit = "account.payment.register"

    check_date = fields.Date(string="Cheque Date")
    check_number = fields.Char(string="Cheque Number")
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=True, compute='_compute_amount')
    taxed_amount = fields.Monetary(string='Tax Amount', currency_field='currency_id', store=True, readonly=False)
    # untaxed_amount = fields.Monetary(string='Untaxed Amount', currency_field='currency_id', store=True, readonly=False)
    payment_difference_handling = fields.Selection(
        [
            ('open', 'Keep open'),
            ('reconcile', 'Mark as fully paid'),
            ('reconcile_with_tax', 'Mark as fully paid with tax')
        ],
        compute='_compute_payment_difference_handling',
        store=True,
        readonly=False,
    )
    account_id = fields.Many2one('account.account', string='Tax Account', required=False, check_company=True)

    @api.depends('can_edit_wizard', 'amount', 'installments_mode', 'taxed_amount')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.payment_date:
                total_amount_values = wizard._get_total_amounts_to_pay(wizard.batches)
                if wizard.installments_mode in ('overdue', 'next', 'before_date'):
                    wizard.payment_difference = total_amount_values['amount_for_difference'] - wizard.amount - wizard.taxed_amount
                    # _logger.info("Full Amount for difference: %s", wizard.payment_difference)
                elif wizard.installments_mode == 'full':
                    if wizard.taxed_amount:
                        wizard.payment_difference = total_amount_values['full_amount_for_difference'] - wizard.amount - wizard.taxed_amount
                    else:
                        wizard.payment_difference = total_amount_values['full_amount_for_difference'] - wizard.amount 
                else:
                    wizard.payment_difference = total_amount_values['amount_for_difference'] - wizard.amount - wizard.taxed_amount
                    _logger.info(f"Partial Amount for difference: {wizard.payment_difference},Total Amount: {total_amount_values['amount_for_difference']},")
            else:
                wizard.payment_difference = 0.0

    @api.depends(
        'can_edit_wizard', 'source_amount', 'source_amount_currency',
        'source_currency_id', 'company_id', 'currency_id',
        'payment_date', 'installments_mode', 'taxed_amount'
    )
    def _compute_amount(self):
        for wizard in self:
            if not wizard.journal_id or not wizard.currency_id or not wizard.payment_date or wizard.custom_user_amount:
                wizard.amount = wizard.amount
            else:
                try:
                    total_amount_values = wizard._get_total_amounts_to_pay(wizard.batches) or {}
                except UserError:
                    wizard.amount = 0.0
                    # wizard.untaxed_amount = 0.0
                    continue

                # wizard.untaxed_amount = total_amount_values['amount_by_default'] or 0.0
                wizard.amount = total_amount_values['amount_by_default'] or 0.0
                wizard.amount = wizard.amount - (wizard.taxed_amount or 0.0)

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals.update({
            "check_date": self.check_date,
            "check_number": self.check_number,
            "account_id": self.account_id.id,
            "taxed_amount": self.taxed_amount,
            "payment_difference_handling": self.payment_difference_handling,
        })
        return payment_vals


class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_date = fields.Date(string="Cheque Date", readonly=True)
    check_number = fields.Char(string="Cheque Number", readonly=True)
    account_id = fields.Many2one('account.account', string='Tax Account', check_company=True)
    taxed_amount = fields.Monetary(string='Tax Amount', currency_field='currency_id', store=True)
    # untaxed_amount = fields.Monetary(string='Untaxed Amount', currency_field='currency_id', store=True)
    payment_difference_handling = fields.Selection(
        [
            ('open', 'Keep open'),
            ('reconcile', 'Mark as fully paid'),
            ('reconcile_with_tax', 'Mark as fully paid with tax')
        ],
        string="Payment Difference Handling",
        readonly=True
    )

    @api.model
    def _get_trigger_fields_to_synchronize(self):
        return (
            'date', 'amount', 'payment_type', 'partner_type', 'payment_reference',
            'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'journal_id','taxed_amount', 'account_id',
            'payment_difference_handling'
        )

    def _synchronize_to_moves(self, changed_fields):
        """Extend default move creation to add withholding tax lines."""
        moves = super()._synchronize_to_moves(changed_fields)

        for payment in self:
            if (
                payment.payment_difference_handling == 'reconcile_with_tax'
                and payment.taxed_amount
                and payment.account_id
            ) or (
                payment.payment_difference_handling == 'open'
                and payment.taxed_amount
                and payment.account_id
            ):
                move = payment.move_id

                # Find the receivable line
                receivable_line = move.line_ids.filtered(
                    lambda l: l.account_id.account_type == 'asset_receivable'
                )[:1]
                if not receivable_line:
                    continue

                # Add tax lines if not already present
                existing_tax_lines = move.line_ids.filtered(lambda l: l.name == "Withholding Tax")
                if not existing_tax_lines:
                    move.write({
                        "line_ids": [
                            Command.create({
                                "name": "Withholding Tax",
                                "account_id": payment.account_id.id,
                                "partner_id": payment.partner_id.id,
                                "debit": payment.taxed_amount,
                                "credit": 0.0,
                                "currency_id": payment.currency_id.id,
                                "date_maturity": payment.date,
                            }),
                            Command.create({
                                "name": "Withholding Tax",
                                "account_id": receivable_line.account_id.id,
                                "partner_id": payment.partner_id.id,
                                "debit": 0.0,
                                "credit": payment.taxed_amount,
                                "currency_id": payment.currency_id.id,
                                "date_maturity": payment.date,
                            }),
                        ]
                    })
        return moves
