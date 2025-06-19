import os
from dotenv import load_dotenv
import streamlit as st
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("Please set the GROQ_API_KEY in your .env file.")
    st.stop()

LOCALDB = "USE_LOACAL_DB"
MYSQL = "USE_MYSQL_DB"

st.set_page_config(page_title="SQLBot", page_icon=":robot:", layout="wide")
st.title("SQLBot :robot:")

radio_options = ["Use SQLite3 Database", "Connect to your MySQL Database"]
selected_option = st.sidebar.radio("Select database you want to chat with", radio_options)

if radio_options.index(selected_option) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host", "localhost")
    mysql_user = st.sidebar.text_input("MySQL User", "root")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database Name", "sqlbot")
else:
    db_uri = LOCALDB
    sqlite_db_path = st.sidebar.text_input("SQLite3 Database Path", "./db/sqlbot.db")
    if not os.path.exists(sqlite_db_path):
        st.error("Database file does not exist. Please check the path.")
        st.stop()

if not db_uri:
    st.info("Please select a database option.")

llm = ChatGroq(groq_proxy=GROQ_API_KEY, model="llama3-8b-8192", streaming=True)


@st.cache_resource(ttl="2h")
def get_sql_database(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        creator = lambda: sqlite3.connect(f"file:{sqlite_db_path}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite://", creator=creator))
    elif db_uri == MYSQL:
        if not all([mysql_host, mysql_user, mysql_password, mysql_db]):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(
            create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
        )

if db_uri == MYSQL:
    db = get_sql_database(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = get_sql_database(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
if "messages" not in st.session_state or st.sidebar.button("Clear Chat History"):
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hello! I am SQLBot, your personal SQL assistant. You can ask me anything about the database. How can I assist you today?"
        }
    ]

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

user_query = st.chat_input("Ask anything from the database...")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)