import json

end = """
</managed-schema>
"""

with open('langages.json', 'r', encoding='utf-8') as f:
    langages = json.load(f)

with open("managed-schema-base.xml", 'r', encoding='utf-8') as f:
    base = "".join(f.readlines()[:-1])

with open("managed-schema.xml", 'w', encoding='utf-8') as f:
    f.write(base)
    # Titles part
    f.write("""
    
    <!-- Titles -->
    <field name="best_title" type="text_general" indexed="true" stored="true" multiValued="false"
       termVectors="true" termPositions="true" termOffsets="true" required="true"/>
    <field name="titles" type="text_general" indexed="true" stored="false" multiValued="true"
    termVectors="true" termPositions="true" termOffsets="true"/>      
""")

    for langage in langages:
        f.write(f"""
    <field name="title_{langage.capitalize()}" type="text_{langage}" indexed="true" stored="false" multiValued="false"
        termVectors="true" termPositions="true" termOffsets="true"/>
    <copyField source="title_{langage.capitalize()}" dest="titles" maxChars="4000"/>""")

    # Descriptions part
    f.write("""
    
    
    <!-- Descriptions -->
    <field name="best_description" type="text_general" indexed="true" stored="true" multiValued="false"/>
    <field name="descriptions" type="text_general" indexed="true" stored="false" multiValued="true"/>
""")

    for langage in langages:
        f.write(f"""
    <field name="description_{langage.capitalize()}" type="text_{langage}" indexed="true" stored="false" multiValued="false"/>
    <copyField source="description_{langage.capitalize()}" dest="descriptions" maxChars="4000"/>""")

    # Keywords part
    f.write("""
    
    
    <!-- Keywords (subjects) -->
    <field name="subjects" type="text_general" indexed="true" stored="false" multiValued="true"/>
""")

    for langage in langages:
        f.write(f"""
    <field name="subject_{langage.capitalize()}" type="text_{langage}" indexed="true" stored="false" multiValued="true"/>
    <copyField source="subject_{langage.capitalize()}" dest="subjects" maxChars="4000"/>""")

    # End
    f.write(end)
