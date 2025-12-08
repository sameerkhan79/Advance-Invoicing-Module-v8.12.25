/** @odoo-module **/

import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { ProductVariantDialog } from "./dialog_box";
import { Component, useState, onWillStart } from "@odoo/owl";
import { NoVariantDialog } from "./no_variant_dialog_box";

export class AccountMoveLineProductField extends Many2OneField {
    static template = "account_move_inherit.InvoiceProductField";

    setup() {
        super.setup();
        this.state = useState({
            selected_variant_ids: this.props.record.data.selected_variant_ids || [],
            selected_variant_names: this.props.record.data.selected_variant_names
                ? this.props.record.data.selected_variant_names   // convert CSV to array
                : [],
        });
        this.actionService = useService("action");
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.checkState = this.props.record._parentRecord.data.state

    }

    async _onVariantsSelected({ ids, names }) {
        this.state.selected_variant_ids = ids;
        this.state.selected_variant_names = names;
    }

    async onEditConfiguration() {

        const product_tmpl_id = this.props.record.data.product_template_id?.[0];
        if (!product_tmpl_id) {
            console.warn("No product template selected for configuration.");
            return;
        }

        const variants = await rpc("/get_product_variants", {
            product_tmpl_id,
            line_id: this.props.record.evalContext.id,
        });

        if (!variants || variants.length === 0) {
            this.dialog.add(NoVariantDialog, {
                close: () => {
                    this.actionService.doAction({ type: 'ir.actions.act_window_close' });
                },
            });
            return;
        }
        this.dialog.add(ProductVariantDialog, {
            variants,
            onConfirm: this._onVariantsSelected.bind(this),
            close: () => {
                this.actionService.doAction({ type: 'ir.actions.act_window_close' });
            },
            product_subtotal: this.props.record.data.price_subtotal,
            price_info: this.props.record.data.price_info,
            currency_id: this.props.record.data.currency_id[0],
            line_id: this.props.record.evalContext.id,
            product_id: this.props.record.data.product_id?.[0],
            selected_variant_ids: this.state.selected_variant_ids,
            application_number: this.props.record.data.application_id || {}
        });
    }
}

export const accountMoveLineProductField = {
    ...many2OneField,
    listViewWidth: [240, 400],
    component: AccountMoveLineProductField,
};

registry.category("fields").add("invoice_product_many2one", accountMoveLineProductField);
