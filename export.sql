select
p.name as recipient_name,
p.id as recipient_id, 
g.id as grant_reference,
g.value as amount,
g.title as grant_title,
g.start_date as start_date,
g.end_date as end_date,
g.scheme as grant_scheme,
g.abstract as grant_abstract,
g.final_report_summary as grant_final_report_summary,
d.name as department_name,
d.id as department_id,
o.name as institution_name,
o.id as institution_id
from grants as g 
left join people as p on g.principal_investigator_id = p.id
left join departments as d on g.department_id = d.id 
left join organisations as o on d.organisation_id = o.id
where (start_date is not null and end_date is not null)
order by start_date asc;
