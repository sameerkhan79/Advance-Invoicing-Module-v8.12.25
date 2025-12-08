/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { CheckBox } from "@web/core/checkbox/checkbox";

export class InvoiceLineListRendererWithFieldCheckbox extends ListRenderer {
    static components = { ...ListRenderer.components, CheckBox };
    static recordRowTemplate = "account_move_inherit.ListRenderer.RecordRowWithCheckbox";
    setup() {
        super.setup()
        // console.log('checking out the seqeunce of the fields', this.props.archInfo.columns);
        const columnSequence = this.props.archInfo.columns
        this.visible_columns = columnSequence.filter(col => !col.column_invisible);

        this.columnPriorityMap = {};
        this.visible_columns.forEach((col, index) => {
            this.columnPriorityMap[col.name] = index + 1;
        });

        console.log("Visible column priority map:", this.columnPriorityMap);
    }
    onFieldCheckboxToggle(record, fieldName, ev) {
        const checked = ev.target.checked;
        const recId = record.resId || record.id;

        const newFlags = Object.assign({}, record.data.extra_flags || {});

        if (!newFlags[recId]) {
            newFlags[recId] = [];
        }

        if (checked) {
            if (!newFlags[recId].includes(fieldName)) {
                newFlags[recId].push(fieldName);
            }
        } else {
            newFlags[recId] = newFlags[recId].filter(f => f !== fieldName);
        }

        const priority = this.columnPriorityMap;

        newFlags[recId] = newFlags[recId].sort((a, b) => {
            const pa = priority[a] || 100;
            const pb = priority[b] || 100;
            if (pa !== pb) {
                return pa - pb;
            }
            return a.localeCompare(b);
        });

        record.update({ extra_flags: newFlags });
    }


}

export class InvoiceLineOne2ManyWithFieldCheckbox extends X2ManyField {
    static components = {
        ...X2ManyField.components,
        ListRenderer: InvoiceLineListRendererWithFieldCheckbox,
    };
}

registry.category("fields").add("invoiceLine_list_renderer_with_checkbox", {
    ...x2ManyField,
    component: InvoiceLineOne2ManyWithFieldCheckbox,
});
