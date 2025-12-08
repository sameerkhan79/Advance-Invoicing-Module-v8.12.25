/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class NoVariantDialog extends Component {
    static template = "account_move_inherit.NoVariantDialog";
    static components = { Dialog };
    static props = {
        close: Function,
    };

    setup() {}
    close() {
        this.props.close();
    }
}
