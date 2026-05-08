DROP VIEW IF EXISTS alarm_event_view CASCADE;
CREATE VIEW alarm_event_view AS
 SELECT a.id,
    a.event_desc,
    a.event_time,
    a.equipment_id,
    a.rule_id,
    a.sector_id,
    a.add_time,
    a.event_type,
    a.is_handle,
    b.name,
    b.area_id,
    to_date(to_char(date_trunc('day'::text, a.event_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
    to_date(to_char(date_trunc('week'::text, a.event_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week,
    to_date(to_char(date_trunc('month'::text, a.event_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month,
    date_part('year'::text, a.event_time) AS year
   FROM (public.dataapp_alarmevent a
     LEFT JOIN public.dataapp_monitorsector b ON (((a.sector_id)::text = (b.code)::text)));

DROP VIEW IF EXISTS crkje_day_sum_view CASCADE;
CREATE VIEW crkje_day_sum_view AS
 SELECT aa.day,
    aa.ckje2,
    aa.rkje2,
    (aa.ckje2 + aa.rkje2) AS zje
   FROM ( SELECT a.rq2 AS day,
            (a.ckje)::numeric AS ckje,
            (b.rkje)::numeric AS rkje,
                CASE
                    WHEN (a.ckje IS NULL) THEN (0)::numeric
                    ELSE (a.ckje)::numeric
                END AS ckje2,
                CASE
                    WHEN (b.rkje IS NULL) THEN (0)::numeric
                    ELSE (b.rkje)::numeric
                END AS rkje2
           FROM (( SELECT dataapp_outmoney.gzrq AS rq,
                    to_date((dataapp_outmoney.gzrq)::text, 'YYYY/MM/DD'::text) AS rq2,
                    sum(dataapp_outmoney.je) AS ckje
                   FROM public.dataapp_outmoney
                  GROUP BY dataapp_outmoney.gzrq
                  ORDER BY (to_date((dataapp_outmoney.gzrq)::text, 'YYYY/MM/DD'::text))) a
             LEFT JOIN ( SELECT dataapp_inmoney.rkrq AS rq,
                    to_date((dataapp_inmoney.rkrq)::text, 'YYYY/MM/DD'::text) AS rq2,
                    sum(dataapp_inmoney.shje) AS rkje
                   FROM public.dataapp_inmoney
                  GROUP BY dataapp_inmoney.rkrq
                  ORDER BY (to_date((dataapp_inmoney.rkrq)::text, 'YYYY/MM/DD'::text))) b ON ((a.rq2 = b.rq2)))
          ORDER BY a.rq2) aa;

DROP VIEW IF EXISTS crkje_month_sum_view CASCADE;
CREATE VIEW crkje_month_sum_view AS
 SELECT a.month,
    sum(a.ckje2) AS ckje2,
    sum(a.rkje2) AS rkje2,
    sum(a.zje) AS zje
   FROM ( SELECT crkje_day_sum_view.day,
            crkje_day_sum_view.ckje2,
            crkje_day_sum_view.rkje2,
            crkje_day_sum_view.zje,
            to_date(to_char(date_trunc('month'::text, (crkje_day_sum_view.day)::timestamp with time zone), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS month
           FROM public.crkje_day_sum_view) a
  GROUP BY a.month
  ORDER BY a.month;

DROP VIEW IF EXISTS crkje_week_sum_view CASCADE;
CREATE VIEW crkje_week_sum_view AS
 SELECT a.week,
    sum(a.ckje2) AS ckje2,
    sum(a.rkje2) AS rkje2,
    sum(a.zje) AS zje
   FROM ( SELECT crkje_day_sum_view.day,
            crkje_day_sum_view.ckje2,
            crkje_day_sum_view.rkje2,
            crkje_day_sum_view.zje,
            to_date(to_char(date_trunc('week'::text, (crkje_day_sum_view.day)::timestamp with time zone), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week
           FROM public.crkje_day_sum_view) a
  GROUP BY a.week
  ORDER BY a.week;

DROP VIEW IF EXISTS crkje_year_sum_view CASCADE;
CREATE VIEW crkje_year_sum_view AS
 SELECT a.year,
    sum(a.ckje2) AS ckje2,
    sum(a.rkje2) AS rkje2,
    sum(a.zje) AS zje
   FROM ( SELECT crkje_day_sum_view.day,
            crkje_day_sum_view.ckje2,
            crkje_day_sum_view.rkje2,
            crkje_day_sum_view.zje,
            date_part('year'::text, crkje_day_sum_view.day) AS year
           FROM public.crkje_day_sum_view) a
  GROUP BY a.year
  ORDER BY a.year;

DROP VIEW IF EXISTS hw_cdz_ammeter_day_hour_view CASCADE;
CREATE VIEW hw_cdz_ammeter_day_hour_view AS
 SELECT dataapp_ammeterindexvalue.start_time,
    dataapp_ammeterindexvalue.end_time,
    dataapp_ammeterindexvalue.ammeter_id,
    dataapp_ammeterindexvalue.address,
    round((dataapp_ammeterindexvalue.zygdnsz)::numeric, 2) AS zygdnsz,
    dataapp_ammeterindexvalue.radio,
    round(((dataapp_ammeterindexvalue.zygdnsz - lag(dataapp_ammeterindexvalue.zygdnsz, 1) OVER (PARTITION BY dataapp_ammeterindexvalue.ammeter_id, dataapp_ammeterindexvalue.address, dataapp_ammeterindexvalue.radio ORDER BY dataapp_ammeterindexvalue.start_time)))::numeric, 2) AS h_zygdnsz
   FROM public.dataapp_ammeterindexvalue
  WHERE ((dataapp_ammeterindexvalue.data_source = 1) AND (((dataapp_ammeterindexvalue.ammeter_id)::text = '20210800670'::text) OR ((dataapp_ammeterindexvalue.ammeter_id)::text = '20210800493'::text)))
  ORDER BY dataapp_ammeterindexvalue.ammeter_id, dataapp_ammeterindexvalue.start_time;

DROP VIEW IF EXISTS hw_cdz_area_day_hour_sum_view CASCADE;
CREATE VIEW hw_cdz_area_day_hour_sum_view AS
 SELECT 29713 AS area_id,
    '点12-充电桩'::text AS area_name,
    a.day,
    a.hour,
    round(sum(a.h_zygdnsz), 2) AS zygdnsz
   FROM ( SELECT hw_cdz_ammeter_day_hour_view.h_zygdnsz,
            to_date(to_char(date_trunc('day'::text, hw_cdz_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
            date_part('hour'::text, hw_cdz_ammeter_day_hour_view.start_time) AS hour
           FROM public.hw_cdz_ammeter_day_hour_view) a
  GROUP BY a.day, a.hour
  ORDER BY a.day, a.hour;

DROP VIEW IF EXISTS hw_cdz_area_day_sum_view CASCADE;
CREATE VIEW hw_cdz_area_day_sum_view AS
 SELECT 29713 AS area_id,
    '点12-充电桩'::text AS area_name,
    a.day,
    round(sum(a.h_zygdnsz), 2) AS zygdnsz
   FROM ( SELECT hw_cdz_ammeter_day_hour_view.h_zygdnsz,
            to_date(to_char(date_trunc('day'::text, hw_cdz_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day
           FROM public.hw_cdz_ammeter_day_hour_view) a
  GROUP BY a.day
  ORDER BY a.day;

DROP VIEW IF EXISTS hw_cdz_area_month_sum_view CASCADE;
CREATE VIEW hw_cdz_area_month_sum_view AS
 SELECT 29713 AS area_id,
    '点12-充电桩'::text AS area_name,
    a.month,
    round(sum(a.h_zygdnsz), 2) AS zygdnsz
   FROM ( SELECT hw_cdz_ammeter_day_hour_view.h_zygdnsz,
            to_date(to_char(date_trunc('month'::text, hw_cdz_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month
           FROM public.hw_cdz_ammeter_day_hour_view) a
  GROUP BY a.month
  ORDER BY a.month;

DROP VIEW IF EXISTS hw_cdz_area_week_sum_view CASCADE;
CREATE VIEW hw_cdz_area_week_sum_view AS
 SELECT 29713 AS area_id,
    '点12-充电桩'::text AS area_name,
    a.week,
    round(sum(a.h_zygdnsz), 2) AS zygdnsz
   FROM ( SELECT hw_cdz_ammeter_day_hour_view.h_zygdnsz,
            to_date(to_char(date_trunc('week'::text, hw_cdz_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week
           FROM public.hw_cdz_ammeter_day_hour_view) a
  GROUP BY a.week
  ORDER BY a.week;

DROP VIEW IF EXISTS hw_cdz_area_year_sum_view CASCADE;
CREATE VIEW hw_cdz_area_year_sum_view AS
 SELECT 29713 AS area_id,
    '点12-充电桩'::text AS area_name,
    a.year,
    round(sum(a.h_zygdnsz), 2) AS zygdnsz
   FROM ( SELECT hw_cdz_ammeter_day_hour_view.h_zygdnsz,
            date_part('year'::text, hw_cdz_ammeter_day_hour_view.start_time) AS year
           FROM public.hw_cdz_ammeter_day_hour_view) a
  GROUP BY a.year
  ORDER BY a.year;

DROP VIEW IF EXISTS hw_gf_ammeter_day_hour_view CASCADE;
CREATE VIEW hw_gf_ammeter_day_hour_view AS
 SELECT aa.start_time,
    aa.end_time,
    aa.ammeter_id,
    aa.address,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.nygdnsz,
    aa.radio,
    aa.h_nygdnsz,
        CASE
            WHEN ((aa.h_nygdnsz < (0)::numeric) OR (aa.h_nygdnsz > (2000)::numeric)) THEN (0)::numeric
            ELSE aa.h_nygdnsz
        END AS h_nygdnsz2,
        CASE
            WHEN (((aa.ammeter_id)::text = '20210800527'::text) OR ((aa.ammeter_id)::text = '20210800657'::text)) THEN 29712
            WHEN ((aa.ammeter_id)::text = '20230200818'::text) THEN 29714
            ELSE NULL::integer
        END AS area_id,
        CASE
            WHEN (((aa.ammeter_id)::text = '20210800527'::text) OR ((aa.ammeter_id)::text = '20210800657'::text)) THEN '点11-二期光伏发电'::text
            WHEN ((aa.ammeter_id)::text = '20230200818'::text) THEN '点13-一期光伏发电'::text
            ELSE NULL::text
        END AS area_name
   FROM ( SELECT a.start_time,
            a.end_time,
            a.ammeter_id,
            a.address,
            a.zygdnsz,
            a.fygdnsz,
            a.nygdnsz,
            a.radio,
            round((a.nygdnsz - lag(a.nygdnsz, 1) OVER (PARTITION BY a.ammeter_id, a.address, a.radio ORDER BY a.start_time)), 2) AS h_nygdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.start_time,
                    dataapp_ammeterindexvalue.end_time,
                    dataapp_ammeterindexvalue.ammeter_id,
                    dataapp_ammeterindexvalue.address,
                    round(((dataapp_ammeterindexvalue.zygdnsz - dataapp_ammeterindexvalue.fygdnsz))::numeric, 2) AS nygdnsz,
                    round((dataapp_ammeterindexvalue.zygdnsz)::numeric, 2) AS zygdnsz,
                    round((dataapp_ammeterindexvalue.fygdnsz)::numeric, 2) AS fygdnsz,
                    dataapp_ammeterindexvalue.radio
                   FROM public.dataapp_ammeterindexvalue
                  WHERE ((dataapp_ammeterindexvalue.data_source = 1) AND (((dataapp_ammeterindexvalue.ammeter_id)::text = '20210800527'::text) OR ((dataapp_ammeterindexvalue.ammeter_id)::text = '20210800657'::text) OR ((dataapp_ammeterindexvalue.ammeter_id)::text = '20230200818'::text)))
                  ORDER BY dataapp_ammeterindexvalue.ammeter_id, dataapp_ammeterindexvalue.start_time) a) aa;

DROP VIEW IF EXISTS hw_gf_area_day_hour_sum_view CASCADE;
CREATE VIEW hw_gf_area_day_hour_sum_view AS
 SELECT a.area_id,
    a.area_name,
    a.day,
    a.hour,
    round(sum(a.h_nygdnsz), 2) AS nygdnsz,
    round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
   FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
            hw_gf_ammeter_day_hour_view.h_nygdnsz2,
            to_date(to_char(date_trunc('day'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
            date_part('hour'::text, hw_gf_ammeter_day_hour_view.start_time) AS hour,
            hw_gf_ammeter_day_hour_view.area_id,
            hw_gf_ammeter_day_hour_view.area_name
           FROM public.hw_gf_ammeter_day_hour_view) a
  GROUP BY a.area_id, a.area_name, a.day, a.hour
  ORDER BY a.area_id, a.area_name, a.day, a.hour;

DROP VIEW IF EXISTS hw_gf_area_day_sum_view CASCADE;
CREATE VIEW hw_gf_area_day_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.day,
    aa.nygdnsz,
    aa.nygdnsz2,
    aa.nygdnsz3,
    round((aa.nygdnsz3 - lag(aa.nygdnsz3, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day)), 2) AS nygdnsz3_dif,
        CASE
            WHEN (lag(aa.nygdnsz3, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz3 - lag(aa.nygdnsz3, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day)) / lag(aa.nygdnsz3, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day)), 3)
        END AS nygdnsz3_ratio
   FROM ( SELECT b.area_id,
            b.area_name,
            b.day,
            b.nygdnsz,
            b.nygdnsz2,
                CASE
                    WHEN ((b.nygdnsz < (0)::numeric) OR (b.nygdnsz > (15000)::numeric)) THEN b.nygdnsz2
                    ELSE b.nygdnsz
                END AS nygdnsz3
           FROM ( SELECT a.area_id,
                    a.area_name,
                    a.day,
                    round(sum(a.h_nygdnsz), 2) AS nygdnsz,
                    round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
                   FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                            hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                            to_date(to_char(date_trunc('day'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
                            hw_gf_ammeter_day_hour_view.area_id,
                            hw_gf_ammeter_day_hour_view.area_name
                           FROM public.hw_gf_ammeter_day_hour_view) a
                  GROUP BY a.area_id, a.area_name, a.day
                  ORDER BY a.area_id, a.area_name, a.day) b) aa;

DROP VIEW IF EXISTS hw_gf_area_month_sum_view CASCADE;
CREATE VIEW hw_gf_area_month_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.month,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month)) / lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.month,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    to_date(to_char(date_trunc('month'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month,
                    hw_gf_ammeter_day_hour_view.area_id,
                    hw_gf_ammeter_day_hour_view.area_name
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.area_id, a.area_name, a.month
          ORDER BY a.area_id, a.area_name, a.month) aa;

DROP VIEW IF EXISTS hw_gf_area_week_sum_view CASCADE;
CREATE VIEW hw_gf_area_week_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.week,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week)) / lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.week,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    to_date(to_char(date_trunc('week'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week,
                    hw_gf_ammeter_day_hour_view.area_id,
                    hw_gf_ammeter_day_hour_view.area_name
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.area_id, a.area_name, a.week
          ORDER BY a.area_id, a.area_name, a.week) aa;

DROP VIEW IF EXISTS hw_gf_area_year_sum_view CASCADE;
CREATE VIEW hw_gf_area_year_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.year,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year)) / lag(aa.nygdnsz2, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.year,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    date_part('year'::text, hw_gf_ammeter_day_hour_view.start_time) AS year,
                    hw_gf_ammeter_day_hour_view.area_id,
                    hw_gf_ammeter_day_hour_view.area_name
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.area_id, a.area_name, a.year
          ORDER BY a.area_id, a.area_name, a.year) aa;

DROP VIEW IF EXISTS hw_gf_day_hour_sum_view CASCADE;
CREATE VIEW hw_gf_day_hour_sum_view AS
 SELECT a.day,
    a.hour,
    round(sum(a.h_nygdnsz), 2) AS nygdnsz,
    round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
   FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
            hw_gf_ammeter_day_hour_view.h_nygdnsz2,
            to_date(to_char(date_trunc('day'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
            date_part('hour'::text, hw_gf_ammeter_day_hour_view.start_time) AS hour
           FROM public.hw_gf_ammeter_day_hour_view) a
  GROUP BY a.day, a.hour
  ORDER BY a.day, a.hour;

DROP VIEW IF EXISTS hw_gf_day_sum_view CASCADE;
CREATE VIEW hw_gf_day_sum_view AS
 SELECT aa.day,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.day)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.day) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.day)) / lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.day)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.day,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    to_date(to_char(date_trunc('day'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.day
          ORDER BY a.day) aa;

DROP VIEW IF EXISTS hw_gf_month_sum_view CASCADE;
CREATE VIEW hw_gf_month_sum_view AS
 SELECT aa.month,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.month)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.month) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.month)) / lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.month)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.month,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    to_date(to_char(date_trunc('month'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.month
          ORDER BY a.month) aa;

DROP VIEW IF EXISTS hw_gf_week_sum_view CASCADE;
CREATE VIEW hw_gf_week_sum_view AS
 SELECT aa.week,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.week)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.week) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.week)) / lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.week)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.week,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    to_date(to_char(date_trunc('week'::text, hw_gf_ammeter_day_hour_view.start_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.week
          ORDER BY a.week) aa;

DROP VIEW IF EXISTS hw_gf_year_sum_view CASCADE;
CREATE VIEW hw_gf_year_sum_view AS
 SELECT aa.year,
    aa.nygdnsz,
    aa.nygdnsz2,
    round((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.year)), 2) AS nygdnsz2_dif,
        CASE
            WHEN (lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.year) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.nygdnsz2 - lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.year)) / lag(aa.nygdnsz2, 1) OVER (ORDER BY aa.year)), 3)
        END AS nygdnsz2_ratio
   FROM ( SELECT a.year,
            round(sum(a.h_nygdnsz), 2) AS nygdnsz,
            round(sum(a.h_nygdnsz2), 2) AS nygdnsz2
           FROM ( SELECT hw_gf_ammeter_day_hour_view.h_nygdnsz,
                    hw_gf_ammeter_day_hour_view.h_nygdnsz2,
                    date_part('year'::text, hw_gf_ammeter_day_hour_view.start_time) AS year
                   FROM public.hw_gf_ammeter_day_hour_view) a
          GROUP BY a.year
          ORDER BY a.year) aa;

DROP VIEW IF EXISTS vedio_alarm_event_view CASCADE;
CREATE VIEW vedio_alarm_event_view AS
 SELECT a.id,
    a.event_type,
    a.event_desc,
    a.event_time,
    a.is_handle,
    a.equipment_id,
    b.location,
    b.f_area,
    b.video_url,
    b.status,
    b.b_model,
    b.brand,
    b.install_height,
    b.install_method,
    b.install_time,
    b.install_x,
    b.install_y,
    b.ip_address,
    b.pixel,
    b.vedio_type,
    b.f_area_type,
    to_date(to_char(date_trunc('day'::text, a.event_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
    to_date(to_char(date_trunc('week'::text, a.event_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week,
    to_date(to_char(date_trunc('month'::text, a.event_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month,
    date_part('year'::text, a.event_time) AS year
   FROM (public.dataapp_vedioalarmevent a
     LEFT JOIN public.dataapp_videomonitor b ON ((a.equipment_id = b.id)));

DROP VIEW IF EXISTS yj_ammeter_day_hour_sum_view CASCADE;
CREATE VIEW yj_ammeter_day_hour_sum_view AS
 SELECT a.ammeter_id,
    a.ammeter_name,
    a.address,
    a.area_id,
    a.area_name,
    a.day,
    a.hour,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            dataapp_ammeterindexvalue.ammeter_id,
            dataapp_ammeterindexvalue.ammeter_name,
            dataapp_ammeterindexvalue.address,
            dataapp_ammeterindexvalue.area_id,
            dataapp_ammeterindexvalue.area_name,
            to_date(to_char(date_trunc('day'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
            date_part('hour'::text, dataapp_ammeterindexvalue.reading_time) AS hour
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.ammeter_id, a.ammeter_name, a.address, a.area_id, a.area_name, a.day, a.hour
  ORDER BY a.ammeter_id, a.day, a.hour;

DROP VIEW IF EXISTS yj_ammeter_day_sum_view CASCADE;
CREATE VIEW yj_ammeter_day_sum_view AS
 SELECT a.ammeter_id,
    a.ammeter_name,
    a.address,
    a.area_id,
    a.area_name,
    a.day,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            dataapp_ammeterindexvalue.ammeter_id,
            dataapp_ammeterindexvalue.ammeter_name,
            dataapp_ammeterindexvalue.address,
            dataapp_ammeterindexvalue.area_id,
            dataapp_ammeterindexvalue.area_name,
            to_date(to_char(date_trunc('day'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.ammeter_id, a.ammeter_name, a.address, a.area_id, a.area_name, a.day
  ORDER BY a.ammeter_id, a.day;

DROP VIEW IF EXISTS yj_ammeter_month_sum_view CASCADE;
CREATE VIEW yj_ammeter_month_sum_view AS
 SELECT a.ammeter_id,
    a.ammeter_name,
    a.address,
    a.area_id,
    a.area_name,
    a.month,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            dataapp_ammeterindexvalue.ammeter_id,
            dataapp_ammeterindexvalue.ammeter_name,
            dataapp_ammeterindexvalue.address,
            dataapp_ammeterindexvalue.area_id,
            dataapp_ammeterindexvalue.area_name,
            to_date(to_char(date_trunc('month'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.ammeter_id, a.ammeter_name, a.address, a.area_id, a.area_name, a.month
  ORDER BY a.ammeter_id, a.month;

DROP VIEW IF EXISTS yj_ammeter_week_sum_view CASCADE;
CREATE VIEW yj_ammeter_week_sum_view AS
 SELECT a.ammeter_id,
    a.ammeter_name,
    a.address,
    a.area_id,
    a.area_name,
    a.week,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            dataapp_ammeterindexvalue.ammeter_id,
            dataapp_ammeterindexvalue.ammeter_name,
            dataapp_ammeterindexvalue.address,
            dataapp_ammeterindexvalue.area_id,
            dataapp_ammeterindexvalue.area_name,
            to_date(to_char(date_trunc('week'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.ammeter_id, a.ammeter_name, a.address, a.area_id, a.area_name, a.week
  ORDER BY a.ammeter_id, a.week;

DROP VIEW IF EXISTS yj_ammeter_year_sum_view CASCADE;
CREATE VIEW yj_ammeter_year_sum_view AS
 SELECT a.ammeter_id,
    a.ammeter_name,
    a.address,
    a.area_id,
    a.area_name,
    a.year,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            dataapp_ammeterindexvalue.ammeter_id,
            dataapp_ammeterindexvalue.ammeter_name,
            dataapp_ammeterindexvalue.address,
            dataapp_ammeterindexvalue.area_id,
            dataapp_ammeterindexvalue.area_name,
            date_part('year'::text, dataapp_ammeterindexvalue.reading_time) AS year
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.ammeter_id, a.ammeter_name, a.address, a.area_id, a.area_name, a.year
  ORDER BY a.ammeter_id, a.year;

DROP VIEW IF EXISTS yj_area_day_hour_sum_view CASCADE;
CREATE VIEW yj_area_day_hour_sum_view AS
 SELECT a.area_id,
    a.area_name,
    a.day,
    a.hour,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            dataapp_ammeterindexvalue.ammeter_id,
            dataapp_ammeterindexvalue.ammeter_name,
            dataapp_ammeterindexvalue.address,
            dataapp_ammeterindexvalue.area_id,
            dataapp_ammeterindexvalue.area_name,
            to_date(to_char(date_trunc('day'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
            date_part('hour'::text, dataapp_ammeterindexvalue.reading_time) AS hour
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.area_id, a.area_name, a.day, a.hour
  ORDER BY a.area_id, a.day, a.hour;

DROP VIEW IF EXISTS yj_area_day_sum_view CASCADE;
CREATE VIEW yj_area_day_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.day,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day)) / lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.day)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.day,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    dataapp_ammeterindexvalue.ammeter_id,
                    dataapp_ammeterindexvalue.ammeter_name,
                    dataapp_ammeterindexvalue.address,
                    dataapp_ammeterindexvalue.area_id,
                    dataapp_ammeterindexvalue.area_name,
                    to_date(to_char(date_trunc('day'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.area_id, a.area_name, a.day
          ORDER BY a.area_id, a.day) aa;

DROP VIEW IF EXISTS yj_area_month_sum_view CASCADE;
CREATE VIEW yj_area_month_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.month,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month)) / lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.month)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.month,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    dataapp_ammeterindexvalue.ammeter_id,
                    dataapp_ammeterindexvalue.ammeter_name,
                    dataapp_ammeterindexvalue.address,
                    dataapp_ammeterindexvalue.area_id,
                    dataapp_ammeterindexvalue.area_name,
                    to_date(to_char(date_trunc('month'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.area_id, a.area_name, a.month
          ORDER BY a.area_id, a.month) aa;

DROP VIEW IF EXISTS yj_area_week_sum_view CASCADE;
CREATE VIEW yj_area_week_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.week,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week)) / lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.week)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.week,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    dataapp_ammeterindexvalue.ammeter_id,
                    dataapp_ammeterindexvalue.ammeter_name,
                    dataapp_ammeterindexvalue.address,
                    dataapp_ammeterindexvalue.area_id,
                    dataapp_ammeterindexvalue.area_name,
                    to_date(to_char(date_trunc('week'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.area_id, a.area_name, a.week
          ORDER BY a.area_id, a.week) aa;

DROP VIEW IF EXISTS yj_area_year_sum_view CASCADE;
CREATE VIEW yj_area_year_sum_view AS
 SELECT aa.area_id,
    aa.area_name,
    aa.year,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year)) / lag(aa.zygdn, 1) OVER (PARTITION BY aa.area_id, aa.area_name ORDER BY aa.year)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.area_id,
            a.area_name,
            a.year,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    dataapp_ammeterindexvalue.ammeter_id,
                    dataapp_ammeterindexvalue.ammeter_name,
                    dataapp_ammeterindexvalue.address,
                    dataapp_ammeterindexvalue.area_id,
                    dataapp_ammeterindexvalue.area_name,
                    date_part('year'::text, dataapp_ammeterindexvalue.reading_time) AS year
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.area_id, a.area_name, a.year
          ORDER BY a.area_id, a.year) aa;

DROP VIEW IF EXISTS yj_day_hour_sum_view CASCADE;
CREATE VIEW yj_day_hour_sum_view AS
 SELECT a.day,
    a.hour,
    round((sum(a.zygdn))::numeric, 2) AS zygdn,
    round((sum(a.fygdn))::numeric, 2) AS fygdn,
    round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
    round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
    round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
    round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
    round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
    round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
   FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
            dataapp_ammeterindexvalue.fygdn,
            dataapp_ammeterindexvalue.zwgdn,
            dataapp_ammeterindexvalue.fwgdn,
            dataapp_ammeterindexvalue.zygdnsz,
            dataapp_ammeterindexvalue.fygdnsz,
            dataapp_ammeterindexvalue.zwgdnsz,
            dataapp_ammeterindexvalue.fwgdnsz,
            dataapp_ammeterindexvalue.reading_time,
            to_date(to_char(date_trunc('day'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day,
            date_part('hour'::text, dataapp_ammeterindexvalue.reading_time) AS hour
           FROM public.dataapp_ammeterindexvalue
          WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
  GROUP BY a.day, a.hour
  ORDER BY a.day, a.hour;

DROP VIEW IF EXISTS yj_day_sum_view CASCADE;
CREATE VIEW yj_day_sum_view AS
 SELECT aa.day,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.day)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (ORDER BY aa.day) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.day)) / lag(aa.zygdn, 1) OVER (ORDER BY aa.day)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.day,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    to_date(to_char(date_trunc('day'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS day
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.day
          ORDER BY a.day) aa;

DROP VIEW IF EXISTS yj_month_sum_view CASCADE;
CREATE VIEW yj_month_sum_view AS
 SELECT aa.month,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.month)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (ORDER BY aa.month) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.month)) / lag(aa.zygdn, 1) OVER (ORDER BY aa.month)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.month,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    to_date(to_char(date_trunc('month'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM'::text) AS month
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.month
          ORDER BY a.month) aa;

DROP VIEW IF EXISTS yj_week_sum_view CASCADE;
CREATE VIEW yj_week_sum_view AS
 SELECT aa.week,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.week)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (ORDER BY aa.week) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.week)) / lag(aa.zygdn, 1) OVER (ORDER BY aa.week)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.week,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    to_date(to_char(date_trunc('week'::text, dataapp_ammeterindexvalue.reading_time), 'YYYY-MM-DD'::text), 'YYYY-MM-DD'::text) AS week
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.week
          ORDER BY a.week) aa;

DROP VIEW IF EXISTS yj_year_sum_view CASCADE;
CREATE VIEW yj_year_sum_view AS
 SELECT aa.year,
    aa.zygdn,
    aa.fygdn,
    aa.zwgdn,
    aa.fwgdn,
    aa.zygdnsz,
    aa.fygdnsz,
    aa.zwgdnsz,
    aa.fwgdnsz,
    round((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.year)), 2) AS zygdn_dif,
        CASE
            WHEN (lag(aa.zygdn, 1) OVER (ORDER BY aa.year) = (0)::numeric) THEN NULL::numeric
            ELSE round(((aa.zygdn - lag(aa.zygdn, 1) OVER (ORDER BY aa.year)) / lag(aa.zygdn, 1) OVER (ORDER BY aa.year)), 3)
        END AS zygdn_ratio
   FROM ( SELECT a.year,
            round((sum(a.zygdn))::numeric, 2) AS zygdn,
            round((sum(a.fygdn))::numeric, 2) AS fygdn,
            round((sum(a.zwgdn))::numeric, 2) AS zwgdn,
            round((sum(a.fwgdn))::numeric, 2) AS fwgdn,
            round((sum(a.zygdnsz))::numeric, 2) AS zygdnsz,
            round((sum(a.fygdnsz))::numeric, 2) AS fygdnsz,
            round((sum(a.zwgdnsz))::numeric, 2) AS zwgdnsz,
            round((sum(a.fwgdnsz))::numeric, 2) AS fwgdnsz
           FROM ( SELECT dataapp_ammeterindexvalue.zygdn,
                    dataapp_ammeterindexvalue.fygdn,
                    dataapp_ammeterindexvalue.zwgdn,
                    dataapp_ammeterindexvalue.fwgdn,
                    dataapp_ammeterindexvalue.zygdnsz,
                    dataapp_ammeterindexvalue.fygdnsz,
                    dataapp_ammeterindexvalue.zwgdnsz,
                    dataapp_ammeterindexvalue.fwgdnsz,
                    dataapp_ammeterindexvalue.reading_time,
                    date_part('year'::text, dataapp_ammeterindexvalue.reading_time) AS year
                   FROM public.dataapp_ammeterindexvalue
                  WHERE (dataapp_ammeterindexvalue.data_source = 0)) a
          GROUP BY a.year
          ORDER BY a.year) aa;
