MODEL(
    name silver.dim_paayment_term,
    kind FULL,
    cron '@weekly',
    grain (id)
);

SELECT id, name ->> 'en_US' AS name, note ->> 'en_US' AS note
FROM bronze.raw__account_payment_term;
