/** odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { ListController } from "@web/views/list/list_controller";
import {
    Component,
    onMounted,
    onWillPatch,
    onWillRender,
    onWillStart,
    useEffect,
    useRef,
    useState,
    useSubEnv,
} from "@odoo/owl";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { CheckBox } from "@web/core/checkbox/checkbox";

export class ActiveFields extends Component {
    static template = "account_move_inherit.ActiveFields"
    static props = {
        ...standardFieldProps,
    }
    static components = {
        Many2XAutocomplete,
        CheckBox,
    };
    setup() {
        // console.log('this.env', this.props.record.data);
        this.getDomain = () => {
            return [["partner_id", "=", this.props.record.data.partner_id]];
        };

        this.onUpdateTrademark = async (value) => {
            let newVal = false;
            if (value && value.length) {
                const rec = value[0];
                newVal = [rec.id, rec.display_name];
            }
            await this.props.record.update({ trademark_id: newVal });

        };

    }

    onToggle(ev) {
        const record = this.props.record;
        const fieldName = this.props.name;
        const checked = ev.target.checked;

        const newFlags = Object.assign({}, record.data.extra_flags || {});
        newFlags[fieldName] = checked;

        record.update({ extra_flags: newFlags });
    }

}
export const active_fields = {
    component: ActiveFields
};

registry.category("fields").add("active_fields", active_fields);