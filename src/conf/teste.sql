SELECT
  "minitickets_funcionario"."nome",
  COUNT("minitickets_ticket"."id") AS "analista__id__count"
FROM "minitickets_funcionario"
LEFT OUTER JOIN "minitickets_ticket" ON ( "minitickets_funcionario"."id" = "minitickets_ticket"."analista_id" )
  INNER JOIN "minitickets_ticket" T3 ON ( "minitickets_funcionario"."id" = T3."analista_id" )
WHERE ("minitickets_funcionario"."cargo" = 1  AND T3."data_fechamento" BETWEEN 2014-11-01 02:00:00 and 2014-11-06 02:00:00) GROUP BY "minitickets_funcionario"."nome"