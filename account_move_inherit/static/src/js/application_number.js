/** odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillUpdateProps, onWillStart } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ApplicationNumberField extends Component {
    static template = "account_move_inherit.ApplicationNumberField";
    static props = {
        ...standardFieldProps,
    };
    setup() {

        let initialValue = this.props.record.data[this.props.name];
        // console.log('this', this.props.record.data);

        if (typeof initialValue === "string") {
            try {
                initialValue = JSON.parse(initialValue);
            } catch {
                initialValue = {};
            }
        }

        this.state = useState({
            variant_names: this.props.record.data.selected_variant_names || [],
            values: Object.fromEntries(
                Object.entries(initialValue || {}).filter(([key]) =>
                    (this.props.record.data.selected_variant_names || []).includes(key)
                )
            ),
        });

        // console.log(this.state.variant_names, this.state.values);

    }
    onValueChange(variant_name, newValue) {
        // if (parseInt(newValue) < 0) {
        //     return;
        // }

        // // Update the value for this variant
        this.state.values[variant_name] = newValue || 0;

        // Keep only currently selected variants
        const filteredValues = Object.fromEntries(
            Object.entries(this.state.values).filter(([key]) =>
                this.state.variant_names.includes(key)
            )
        );

        // Replace state and update record
        this.state.values = filteredValues;
        this.props.record.update({
            [this.props.name]: filteredValues,
        });

        console.log("Updated values:", filteredValues);
    }


}

export const application_number_field = {
    component: ApplicationNumberField,
    supportedTypes: ["json"],
};
registry.category("fields").add("application_number_field", application_number_field);
