MODEL(
    name silver.dim_customer,
    kind FULL,
    cron '@weekly',
    grain (id)
);

SELECT id, name, city, property_payment_term_id
FROM bronze.raw__res_partner
WHERE create_uid = 2;


