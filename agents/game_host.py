from collections import deque
from typing import Literal

from pydantic import BaseModel, Field, create_model
from agents.base_agent import BaseAgent
from models.game_models import DynamicGameModelFactory, SummariseRoundComplex
from agents.player_models import BaseResponse
from prompts.prompts import PromptLibrary

class GameMaster(BaseAgent):
    def __init__(self, api_client):
        super().__init__("Host", api_client=api_client)
        self.color = "YELLOW"
        self.round_summaries = deque(maxlen=50)
    
    
    def _system_prompt(self, game_board):
        #TODO spruce up with the other one
        #Used in the wildcard selection
        return ( f"You oversee this game. You help to make the information manageable for the LLMs playing."
                f"PAST SUMARRIES: {"\n".join(self.round_summaries)} "
                 f"#########################"
                 f"Current round: {game_board.context_builder.current_round_formatted(self)}")
    
    
    def choose_agent_based_on_parameter(self, game_board, allowed_names, parameter: str):
        #TODO
        if parameter == "chaotic":
            parameter = ("The most CHAOTIC player is the one that has the most unpredictable actions, and causes the most disruption to the other players. "
        "They are the wild card, and can be both a threat and an asset to the other players. They are often the most entertaining to watch, "
        "but also the most difficult to predict.")
        #---------------
        choice_definition = (Literal[*allowed_names], Field(description=parameter))
        public_reason = (str, Field(description="The public announcement as to why this player was chosen. Give answer in the third person passive voice."))
        fields = {"target_name" : choice_definition, "public_reason" : public_reason}
        response_model = create_model("choose_agent_based_on_parameter", __base__=BaseResponse, **fields)
        user_content = (f"You need to choose a single player that best represents this parameter: '{parameter}'.")
        return self.get_response(user_content, response_model, game_board)
        #---------------
    
    def summariseRound(self, game_board):
        turn = self.api_client.create(
            response_model=SummariseRoundComplex,
            messages=[
                {"role": "system", "content": f"You oversee this game. You help to make the information manageable for the LLMs playing."},
                {"role": "user", "content": f"PAST SUMARRIES: {"\n".join(self.round_summaries)} "
                 f"#########################"
                 f"#########################"
                 f"Summarise the following round: {game_board.context_builder.current_round_formatted(self)} Scores:  {game_board.agent_scores}"}
            ]
        )
        self.round_summaries.append(turn.round_summary)
        return turn
    
    def summarise_game_text(self, context, game_text):
        #used in game circle
        model = DynamicGameModelFactory.cycle_game_compression_model()
        turn = self.api_client.create(
            response_model=model,
            messages=[
                {"role": "system", "content": f"You oversee this game. You help to make the information manageable for the LLMs playing."},
                {"role": "user", "content": f"Previous game context:\n{context}"
                 f"#########################"
                 f"#########################"
                 f"Summarise the following segment: {game_text}"} 
            ]
        )
        print("\n\nContext: \n" + context )
        print("\n\nGame text: \n" + game_text)
        print("\n\nSummary: \n" + turn.summary )
        
        return turn.summary
    
    def select_players(self, question, context, allowed_names, max_choices = 3):
        model = DynamicGameModelFactory.choose_multiple_agents(allowed_names, question, max_choices)
        turn = self.api_client.create(
            response_model=model,
            messages=[
                {"role": "system", "content": f"You oversee this game. We need you to select players based on the question: {question}"},
                {"role": "user", "content": f"Game context:\n{context}"} 
            ]
        )
        return turn.namesToChoose
    
    def create_host_script(self, directive, additional_context, context_explanation, game_context, cot_prompts = None):
        #It's referenced as directive in the model 
        model = DynamicGameModelFactory.host_script_model(cot_prompts)
        turn = self.api_client.create(
            response_model=model,
            messages=[
                #in time we will put personality into the user content- favorites, opinions
                {"role": "system", "content": f"You are the HOST of this game. We need to you to act as host, and the script is your public remarks. "
                 "The host is speaking with the players, but also with an audience in mind. "
                 "ONLY DIALOG - only the script- no direction or scene description. "},
                #Ie the context is the players own recap of their journey- use this 
                {"role": "user", "content": f"Context explaination: {context_explanation}\n\n"
                 f"Additional context:\n{additional_context}"
                 f"Game context : What happened before this point in the round:\n{game_context}"
                 f"Your DIRECTIVE: {directive}",} 
            ]
        )
        #print(turn.thought_process)
        return turn
