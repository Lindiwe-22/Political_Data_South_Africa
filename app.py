import os

import dataset
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError as _SQLAlchemyError


class SQLAlchemyError(_SQLAlchemyError):
    """Concrete database error that preserves useful operation context."""

    def __init__(self, message="A database operation failed", *, query=None):
        super().__init__(message)
        self.message = message
        self.query = query

    def __str__(self):
        if self.query:
            return f"{self.message} (query: {self.query})"
        return self.message

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.message!r}, "
            f"query={self.query!r})"
        )

DATABASE_URI = os.environ.get(
    "DATABASE_URI",
    "postgresql://localhost/madlanga_commission",
)


@st.cache_resource
def get_database():
    return dataset.connect(DATABASE_URI)


db = get_database()


st.set_page_config(
    page_title="SA Political & Mining Data Directory",
    page_icon="🇿🇦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .app-subtitle {
            color: #666;
            font-size: 1.05rem;
            margin-top: -0.5rem;
            margin-bottom: 2rem;
        }

        .section-description {
            color: #666;
            margin-top: -0.5rem;
            margin-bottom: 1.25rem;
        }

        .result-count {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }

        .data-label {
            font-weight: 600;
        }

        footer {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("About")

    st.write(
        """
        This directory provides a searchable interface for exploring
        South African political and mining-related public data.
        """
    )

    st.divider()

    st.subheader("Data directory")

    st.write(
        """
        **People**

        Search political representatives and explore their memberships,
        directorships, business interests and financial interests.
        """
    )

    st.write(
        """
        **Mines**

        Search mining operations by mine name or owner and view available
        ownership and operational information.
        """
    )
    st.write(
        """
        **Political Funding**

        Search declared political party donations, including donor names,
        amounts, and donation type, as published by the IEC.
        """
    )
    st.divider()

    st.caption("SA Political & Mining Data Directory")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("SA Political & Mining Data Directory")

st.markdown(
    '<div class="app-subtitle">'
    "Search and explore South African political and mining data."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------

tab_people, tab_mines, tab_donations, tab_profile = st.tabs(
    ["👤 People", "⛏️ Mines", "💰 Political Funding", "👤 Politician Profile"]
)


with tab_people:
    st.header("People")
    st.markdown(
        '<div class="section-description">'
        "Search political representatives by name."
        "</div>",
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search a person's name",
        key="people_search",
        placeholder="e.g. John Smith",
        label_visibility="collapsed",
    )

    if query:
        try:
            words = query.split()
            conditions = " AND ".join(f"name ILIKE :q{i}" for i in range(len(words)))
            params = {f"q{i}": f"%{w}%" for i, w in enumerate(words)}
            results = list(
                db.query(
                    f"""
                    SELECT *
                    FROM sa_pa_persons
                    WHERE {conditions}
                    ORDER BY name
                    LIMIT 25
                    """,
                    **params,
                )
            )

            st.markdown(
                f'<div class="result-count">{len(results)} result(s)</div>',
                unsafe_allow_html=True,
            )

            if not results:
                st.info("No people matched your search.")

            for person in results:
                name = person.get("name") or "Unnamed person"

                with st.expander(name):
                    if person.get("email"):
                        st.markdown(
                            f"**Email:** {person['email']}"
                        )

                    memberships = list(
                        db.query(
                            """
                            SELECT *
                            FROM sa_pa_memberships
                            WHERE person_id = :pid
                            """,
                            pid=person["popit_id"],
                        )
                    )

                    if memberships:
                        st.subheader("Memberships")

                        for membership in memberships:
                            role = membership.get("role") or "member"
                            organization = (
                                membership.get("organization_name")
                                or "Unknown organization"
                            )

                            st.markdown(
                                f"- **{organization}** — {role}"
                            )

                    directorships = list(
                        db.query(
                            """
                            SELECT *
                            FROM sa_pa_directorships
                            WHERE person_id = :pid
                            """,
                            pid=person["popit_id"],
                        )
                    )

                    if directorships:
                        st.subheader(
                            "Directorships / Business Interests"
                        )

                        for directorship in directorships:
                            company = (
                                directorship.get("company_name")
                                or "Unknown company"
                            )

                            st.markdown(f"- {company}")

                    financial = list(
                        db.query(
                            """
                            SELECT *
                            FROM sa_pa_financial
                            WHERE person_id = :pid
                            """,
                            pid=person["popit_id"],
                        )
                    )

                    if financial:
                        st.subheader("Financial Interests")

                        for interest in financial:
                            company = (
                                interest.get("company_name")
                                or "Unknown company"
                            )
                            nature = interest.get("nature") or ""

                            if nature:
                                st.markdown(
                                    f"- **{company}** — {nature}"
                                )
                            else:
                                st.markdown(f"- **{company}**")

        except (KeyError, _SQLAlchemyError, TypeError) as exc:
            st.error(
                "The people search could not be completed."
            )
            st.caption(str(exc))


# ---------------------------------------------------------------------------
# Mines
# ---------------------------------------------------------------------------

with tab_mines:
    st.header("Mines")
    st.markdown(
        '<div class="section-description">'
        "Search mining operations by mine name or owner."
        "</div>",
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search a mine or owner",
        key="mines_search",
        placeholder="e.g. mine name or company",
        label_visibility="collapsed",
    )

    if query:
        try:
            results = list(
                db.query(
                    """
                    SELECT *
                    FROM sa_mines
                    WHERE mine_name ILIKE :q
                       OR owner ILIKE :q
                    ORDER BY mine_name
                    LIMIT 25
                    """,
                    q=f"%{query}%",
                )
            )

            st.markdown(
                f'<div class="result-count">{len(results)} result(s)</div>',
                unsafe_allow_html=True,
            )

            if not results:
                st.info("No mines matched your search.")

            for mine in results:
                mine_name = mine.get("mine_name") or "Unnamed mine"

                with st.expander(mine_name):
                    st.markdown(
                        f"**Owner:** "
                        f"{mine.get('owner') or 'Not available'}"
                    )

                    st.markdown(
                        f"**Previous owner:** "
                        f"{mine.get('previous_owner') or 'Not available'}"
                    )

                    st.markdown(
                        f"**Mining method:** "
                        f"{mine.get('mining_method') or 'Not available'}"
                    )

                    st.markdown(
                        f"**Commodity:** "
                        f"{mine.get('primary_commodity') or 'Not available'}"
                    )

        except _SQLAlchemyError as exc:
            st.error(
                "The mine search could not be completed."
            )
            st.caption(str(exc))

# ---------------------------------------------------------------------------
# Political Funding
# ---------------------------------------------------------------------------

with tab_donations:
    st.header("Political Funding")
    st.markdown(
        '<div class="section-description">'
        "Search declared donations by party or donor name."
        "</div>",
        unsafe_allow_html=True,
    )
    query: str = st.text_input(
        "Search a party or donor",
        key="donations_search",
        placeholder="e.g. party name or donor",
        label_visibility="collapsed",
    )

    try:
        if query:
            results = list(
                db.query(
                    """
                    SELECT *
                    FROM sa_iec_donations
                    WHERE party_name ILIKE :q
                       OR donor_name ILIKE :q
                    ORDER BY amount_quarter DESC
                    """,
                    q=f"%{query}%",
                )
            )
        else:
            results = list(
                db.query(
                    """
                    SELECT *
                    FROM sa_iec_donations
                    ORDER BY amount_quarter DESC
                    """
                )
            )

        st.markdown(
            f'<div class="result-count">{len(results)} result(s)</div>',
            unsafe_allow_html=True,
        )

        if not results:
            st.info("No donations matched your search.")

        for row in results:
            donor = row.get("donor_name") or "Unknown donor"
            party = row.get("party_name") or "Unknown party"

            with st.expander(f"{donor} → {party}"):
                amount = row.get("amount_quarter")
                st.markdown(
                    f"**Amount this quarter:** "
                    f"{'R{:,.2f}'.format(amount) if amount else 'Not disclosed'}"
                )
                st.markdown(
                    f"**Type:** {row.get('donation_type') or 'Not available'}"
                )
                st.markdown(
                    f"**Date:** {row.get('date_of_receipt') or 'Not available'}"
                )
                st.markdown(
                    f"**Source report:** {row.get('source_file') or 'Not available'}"
                )

    except _SQLAlchemyError as exc:
        st.error("The political funding search could not be completed.")
        st.caption(str(exc))


# ---------------------------------------------------------------------------
# Politician Profile
# ---------------------------------------------------------------------------

with tab_profile:
    st.header("Politician Profile")
    st.markdown(
        '<div class="section-description">'
        "A consolidated view of one person's memberships, business interests, "
        "financial declarations, and any cross-list matches found."
        "</div>",
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search a politician's name",
        key="profile_search",
        placeholder="e.g. Herman Mashaba",
        label_visibility="collapsed",
    )

    if query:
        try:
            words = query.split()
            conditions = " AND ".join(f"name ILIKE :q{i}" for i in range(len(words)))
            params = {f"q{i}": f"%{w}%" for i, w in enumerate(words)}
            people = list(
                db.query(
                    f"SELECT * FROM sa_pa_persons WHERE {conditions} ORDER BY name LIMIT 10",
                    **params,
                )
            )

            if not people:
                st.info("No matching politician found.")

            for person in people:
                st.subheader(person.get("name") or "Unnamed")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Memberships")
                    memberships = list(
                        db.query(
                            "SELECT * FROM sa_pa_memberships WHERE person_id = :pid",
                            pid=person["popit_id"],
                        )
                    )
                    if memberships:
                        for m in memberships:
                            role = m.get("role") or "member"
                            org = m.get("organization_name") or "Unknown organization"
                            st.markdown(f"- **{org}** — {role}")
                    else:
                        st.caption("None on record.")

                    st.subheader("Directorships / Business Interests")
                    directorships = list(
                        db.query(
                            "SELECT * FROM sa_pa_directorships WHERE person_id = :pid",
                            pid=person["popit_id"],
                        )
                    )
                    if directorships:
                        for d in directorships:
                            st.markdown(f"- {d.get('company_name') or 'Unknown company'}")
                    else:
                        st.caption("None on record.")

                with col2:
                    st.subheader("Financial Interests")
                    financial = list(
                        db.query(
                            "SELECT * FROM sa_pa_financial WHERE person_id = :pid",
                            pid=person["popit_id"],
                        )
                    )
                    if financial:
                        for f in financial:
                            company = f.get("company_name") or "Unknown"
                            nature = f.get("nature") or ""
                            st.markdown(f"- **{company}**" + (f" — {nature}" if nature else ""))
                    else:
                        st.caption("None on record.")

                    st.subheader("Cross-List Matches")
                    name_tokens = set((person.get("name") or "").upper().split())
                    all_matches = list(db.query("SELECT * FROM sa_cross_list_matches"))
                    relevant = [
                        m for m in all_matches
                        if m.get("source_a") == "MP" and name_tokens & set((m.get("name_a") or "").upper().split())
                    ]
                    if relevant:
                        for m in relevant:
                            st.markdown(f"- Matches **{m['name_b']}** ({m['source_b']})")
                    else:
                        st.caption("No cross-list matches found.")

                st.subheader("Declared Financial Interests Over Time")
                timeline = list(
                    db.query(
                        "SELECT * FROM sa_wealth_timeline WHERE person_id = :pid ORDER BY year",
                        pid=person["popit_id"],
                    )
                )
                if timeline:
                    import pandas as pd
                    df = pd.DataFrame(timeline)
                    df = df.set_index("year")[["total_declared_value"]]
                    df.columns = ["Total Declared Value (R)"]
                    st.line_chart(df)
                    st.caption(
                        "Shows confirmed total declared value only (per-share prices "
                        "converted using declared share counts where available). "
                        "Some years may show R0 where source disclosures used a format "
                        "that could not be reliably converted to a total - see raw "
                        "financial interests above for those years' entries."
                    )
                else:
                    st.caption("No financial timeline data available.")

                st.divider()

        except _SQLAlchemyError as exc:
            st.error("The profile lookup could not be completed.")
            st.caption(str(exc))




# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()

st.caption(
    "SA Political & Mining Data Directory · "
    "Public-data exploration interface"
)