# ©  2015-2020 Deltatech
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stopped = fields.Boolean(
        string="Stopped",
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )  # se se permite livrare daca nu este facuta plata sau din alt motiv.
    delivery_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pre_advice", "Pre advice"),
            ("in_transit", "In Transit"),
            ("in_warehouse", "In Warehouse"),
            ("in_delivery", "In delivery"),
            ("delivered", "Delivered"),
        ],
        string="State",
        default="draft",
        readonly=False,
    )

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self:
            if picking.state == "done" and not picking.carrier_id:
                picking.write({"delivery_state": "delivered"})

        return res

    @api.depends("move_type", "immediate_transfer", "move_lines.state", "move_lines.picking_id", "stopped")
    def _compute_state(self):
        super(StockPicking, self)._compute_state()
        for picking in self.filtered(lambda p: p.state == "assigned"):
            if picking.stopped:
                picking.state = "waiting"

    def button_validate(self):
        for picking in self:
            if picking.stopped:
                raise UserError(_("The transfer %s is stopped") % picking.name)

        return super(StockPicking, self).button_validate()
