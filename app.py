import os
import streamlit as st
import dataset

DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://localhost/madlanga_commission')
db = dataset.connect(DATABASE_URI)

st.set_page_config(page_title="SA Political & Mining Data Directory", layout="wide")
st.title("SA Political & Mining Data Directory")
st.caption("Search MPs' financial disclosures and mine ownership records")

tab_people, tab_mines = st.tabs(["People", "Mines"])

with tab_people:
    query = st.text_input("Search a person's name", key="people_search")
    if query:
        results = list(db.query(
            "SELECT * FROM sa_pa_persons WHERE name ILIKE :q ORDER BY name LIMIT 25",
            q=f"%{query}%"
        ))
        st.write(f"{len(results)} result(s)")
        for person in results:
            with st.expander(person['name']):
                if person.get('email'):
                    st.write(f"Email: {person['email']}")

                memberships = list(db.query(
                    "SELECT * FROM sa_pa_memberships WHERE person_id = :pid",
                    pid=person['popit_id']
                ))
                if memberships:
                    st.subheader("Memberships")
                    for m in memberships:
                        st.write(f"- {m['organization_name']} ({m.get('role') or 'member'})")

                directorships = list(db.query(
                    "SELECT * FROM sa_pa_directorships WHERE person_id = :pid",
                    pid=person['popit_id']
                ))
                if directorships:
                    st.subheader("Directorships / Business Interests")
                    for d in directorships:
                        st.write(f"- {d['company_name']}")

                financial = list(db.query(
                    "SELECT * FROM sa_pa_financial WHERE person_id = :pid",
                    pid=person['popit_id']
                ))
                if financial:
                    st.subheader("Financial Interests")
                    for f in financial:
                        st.write(f"- {f['company_name']}: {f.get('nature') or ''}")

with tab_mines:
    query = st.text_input("Search a mine or owner", key="mines_search")
    if query:
        results = list(db.query(
                        "SELECT * FROM sa_mines WHERE mine_name ILIKE :q OR owner ILIKE :q ORDER BY mine_name LIMIT 25",
            q=f"%{query}%"
        ))
        st.write(f"{len(results)} result(s)")
        for mine in results:
            with st.expander(mine['mine_name']):
                st.write(f"Owner: {mine.get('owner')}")
                st.write(f"Previous owner: {mine.get('previous_owner')}")
                st.write(f"Mining method: {mine.get('mining_method')}")
                st.write(f"Commodity: {mine.get('primary_commodity')}")