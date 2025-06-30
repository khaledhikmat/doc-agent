from dotenv import load_dotenv
import streamlit as st
import asyncio

# Import all the message part classes
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,
    ModelMessagesTypeAdapter
)

from service.config.envvars import EnvVarsConfigService
from service.crawl.craw4ai import AICrawlService
from service.rag.lightrag import LightRAGService

from agent.doc import doc_agent, DocAgentDeps

load_dotenv()

def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # user-prompt
    if part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)             

async def run_agent_with_streaming(user_input):
    async with doc_agent.run_stream(
        user_input, deps=st.session_state.agent_deps, message_history=st.session_state.messages
    ) as result:
        async for message in result.stream_text(delta=True):  
            yield message

    # Add the new messages to the chat history (including tool calls and responses)
    st.session_state.messages.extend(result.new_messages())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~ Main Function with UI Creation ~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def main():

    # Initialize services
    cfg_svc = EnvVarsConfigService()
    crawl_svc = AICrawlService(cfg_svc)
    rag_svc = LightRAGService(cfg_svc, crawl_svc)

    try:
        agent_deps = DocAgentDeps(ragsvc=rag_svc)

        st.title("Documentation RAG-based Agent")

        # Initialize chat history in session state if not present
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "agent_deps" not in st.session_state:
            st.session_state.agent_deps = agent_deps  

        # Display all messages from the conversation so far
        # Each message is either a ModelRequest or ModelResponse.
        # We iterate over their parts to decide how to display them.
        for msg in st.session_state.messages:
            if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
                for part in msg.parts:
                    display_message_part(part)

        # Chat input for the user
        user_input = st.chat_input("What do you want to know?")

        if user_input:
            # Display user prompt in the UI
            with st.chat_message("user"):
                st.markdown(user_input)

            # Display the assistant's partial response while streaming
            with st.chat_message("assistant"):
                # Create a placeholder for the streaming text
                message_placeholder = st.empty()
                full_response = ""
                
                # Properly consume the async generator with async for
                generator = run_agent_with_streaming(user_input)
                async for message in generator:
                    full_response += message
                    message_placeholder.markdown(full_response + "▌")
                
                # Final response without the cursor
                message_placeholder.markdown(full_response)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        crawl_svc.finalize()
        rag_svc.finalize()

if __name__ == "__main__":
    asyncio.run(main())
