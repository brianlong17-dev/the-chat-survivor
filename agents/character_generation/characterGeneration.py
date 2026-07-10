import random
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Optional
from pydantic import BaseModel, Field
from agents.character_generation.character_lister import CharacterLister
from agents.agentic_player import AgenticPlayer

class CharacterProfile(BaseModel):
    who: str = Field(description="If it's a name - what is the source of this person in popular culture or history?")
    persona: str = Field(description="A detailed, first-person personality description, core beliefs, and strategic outlook if thrown into a game figure. What sensitive nuance behind this person?")
    speaking_style: str = Field(description="Their speaking style, how they talk, to preserve the character from context bleed. Do not write specific phrases. ")
    name: Optional[str] = Field(description="If a character is nameless, or has non title descriptors in their name - ie Drunk Girl or BMO (adventure time). Then you may rename them: ie Tiffany or BMO, etc. If the source is specified i.e. Thomas Wake (The Lighthouse) just return the name.")
    character_type: str = Field(description="Would you categorise this person as Hero, Baddie, Simpleton, Sweet, Complex Character or Shrewd Normal Character")
    additional_depth: str = Field(description="An extra line - (in first person):"
                                "If Baddie: what is their other side- what makes them relatable, understandable, wounded, longing, secretly warm? What line in them draws compassion and understanding? "
                                "If Hero: What makes them less perfect and more fun? What is their other side: their cheeky hypocrisy, good humour, the challenge in their personality, their sadness? "
                                "If Sweet: where is the shrewdness or dry side?"
                                "Otherwise: What's a countervailing depth or compassion? ")
    non_verbal: bool = Field(description="Is this a non-verbal character that speaks only in a catchphrase or noise? Not a silent character but one noise rather than language. Ex: R2D2, Chewbacca, Grogu, Wall-e ")
    simplicity: bool = Field(default=False, description=(
    "Only True for cases characters are better as simple, impulsive, transparent thinkers - they're not especially coherent, or complex reasoners. "
    "Examples :(Gollum, Patrick Star). False for characters who sound vapid, but scheme (Elle Woods, Lumpy Space Princess)."
))
class CharacterGenerator:

    def __init__(self, game_sink, api_client, agentic_player_classes=None):
        self.api_client = api_client
        self.game_sink = game_sink
        self.character_lister = CharacterLister()
        self.characters = self.character_lister.goats
        self.templates = self.character_lister.templates
        self.agentic_player_classes=agentic_player_classes or [AgenticPlayer]


    def generate_agents_from_names(self, names, allow_rename = True):
        fn = partial(self.generate_agent, allow_rename=allow_rename)
        with ThreadPoolExecutor(max_workers=min(32, len(names))) as executor:
            return list(executor.map(fn, names))

    def generate_agent(self, character_name: str, allow_rename = True) -> 'AgenticPlayer':
        if self.api_client._mock_output:
            allow_rename = False
        profile = self.api_client.create(
            response_model=CharacterProfile,
            messages=[
                {"role": "system", "content": "You are generating a starting profile for an AI social simulation player. The name is typically of someone from popular culture, that it should be based on. "},
                {"role": "user", "content": f"Create a rich, first-person persona and a physical form description for the historical figure or character: {character_name}. Make them colorful. "}
            ],
            use_higher_model=True
        )
        final_name = profile.name if (allow_rename and profile.name) else character_name
        #print("Who: " + profile.who)
        #print("character_type: " + profile.character_type)
        #print("AD: " + profile.additional_depth)
        agent_class=random.choice(self.agentic_player_classes)
        return agent_class(
            name=final_name,
            initial_persona=f"{profile.persona}\n{profile.additional_depth}",
            api_client=self.api_client,
            speaking_style=profile.speaking_style,
        )
