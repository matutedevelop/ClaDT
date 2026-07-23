-- This is the model of the fact table `sale_order_line` which every registry represent a sale of
-- a particular product  e.g. 5 apples

MODEL(
    name silver.fact_sale_order_line,
    -- kind INCREMENTAL_BY_TIME_RANGE(
    --     time_column pt.create_date
    -- ),
    kind FULL,
    start '2026-01-01',
    cron '@weekly',
    grain (id)
);


SELECT sol.id AS id, pt.id AS product_id, rp.id AS customer_id  ,so.payment_term_id, sol.state, ,sol.invoice_status, sol.product_uom_qty,
       (sol.qty_invoiced + sol.qty_delivered + sol.qty_to_invoice) AS qty, so.name,
        sol.price_unit, sol.price_total, sol.price_subtotal, sol.create_date, to_char(sol.create_date,'YYMMDD') AS date_id,
       
FROM bronze.raw__sale_order_line sol
JOIN bronze.raw__sale_order so ON sol.order_id = so.id
JOIN bronze.raw__product_product pp ON sol.product_id = pp.id
JOIN bronze.raw__product_template pt ON pp.product_tmpl_id = pt.id
JOIN bronze.raw__res_partner rp ON sol.order_partner_id = rp.id
WHERE sol.company_id = 5
