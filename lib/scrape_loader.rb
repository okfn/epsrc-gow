GRANT_KEYS = %w{ value title }

def update_field(obj, field, value)
  if (x = obj.send(field)) and x != value
    $stderr.puts "WARNING: didn't update field '#{field}' on #{obj}: #{x.inspect} -> #{value.inspect}"
  else
    obj.send(field + '=', value)
  end
end

module ScrapeLoader
  def self.load(d)
    $stderr.puts "Processing #{d['id']}"

    g = Grant.find_or_create_by_id(d['id'])
    update_field g, 'value', d['value']
    update_field g, 'title', d['title']

    pi = Person.find_or_create_by_id(d['pi']['id'])
    update_field pi, 'name', d['pi']['name']

    org = Organisation.find_or_create_by_id(d['organisation']['id'])
    update_field org, 'name', d['organisation']['name']

    dept = Department.find_or_create_by_id(d['department']['id'])
    update_field dept, 'name', d['department']['name']

    g.principal_investigator = pi
    g.organisation = org
    g.department = dept

    pi.save
    org.save
    dept.save
    g.save
  end
end