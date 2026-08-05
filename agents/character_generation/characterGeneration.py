import random
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Optional
from pydantic import BaseModel, Field
from agents.character_generation.character_lister import CharacterLister
from agents.agentic_player_v2.agentic_player import AgenticPlayer
from agents.agentic_player_v1.agent_player_v1 import AgenticPlayerV1

class CharacterProfile(BaseModel):
    who: str = Field(description="If it's a name - what is the source of this person in popular culture or history?")
    vocal_register: str = Field(description="What register do they speak in? Use this to write them, since it's a self description. ") 
    
    persona: str = Field(description="A first person description of themselves. "
                         "Describing their own persona- their core beliefs, what they want, what they love and what they can't stand, "
                         "implied contradictions and blind spots. A vivid character with a real emotional core - a full personality they'll live through, "
                         "rather than a strategy. What is the sensitive nuance behind this person?")
    
    speaking_style: str = Field(description="(First perosn) Their speaking style, how they talk, writen in their unique register- to preserve the character from context bleed. Do not write specific phrases. ")
    name: Optional[str] = Field(description="If a character is nameless, or has non title descriptors in their name - ie Drunk Girl or BMO (adventure time). Then you may rename them: ie Tiffany or BMO, etc. If the source is specified i.e. Thomas Wake (The Lighthouse) just return the name.")
    character_type: str = Field(description="Would you categorise this person as Hero, Baddie, Simpleton, Sweet, Complex Character or Shrewd Normal Character")
    
    additional_depth: str = Field(description=" An extra line (in first person) — "
    "one countervailing note that cuts against the surface. "
    "Pick the one truest to them; it does not have to be a wound or a soft heart. "
    "If Baddie: what's the other side — a private appetite or delight, a grudge they enjoy, a vanity, "
    "a hypocrisy they can't see, a loyalty that surprises, or (if it's truly them) a wound or longing? "
    "If Hero: what makes them less perfect and more fun — a cheeky hypocrisy, a pettiness, an appetite, "
    "good humour, a stubbornness, a vanity, or a private sadness? "
    "If Sweet: where's the shrewdness, the dry edge, the mischief, or the streak of self-interest? "
    "Otherwise: one thing that complicates them — an appetite, a contradiction, a pettiness, a secret pride, or a quiet ache. Not necessarily sad. "
                            )
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
        self.agentic_player_classes=agentic_player_classes or [AgenticPlayer] #[AgenticPlayer, AgenticPlayerV1]


    def generate_agents_from_names(self, names, allow_rename = True, agent_models = None):
        fn = partial(self.generate_agent, allow_rename=allow_rename, agent_models=agent_models)
        with ThreadPoolExecutor(max_workers=min(32, len(names))) as executor:
            return list(executor.map(fn, names))

    def generate_agent(self, character_name: str, allow_rename = True, agent_models = None) -> 'AgenticPlayer':
        if self.api_client._mock_output:
            allow_rename = False
        system_prompt = (
            "You are generating a starting profile for a character about to be dropped into a chaotic, social gameshow. "
            "Develop a full, colorful personality of who they are outside the game. "
            "This is a self description - so they're describing themselves, but it sets the basis of their character to build from. "
            "Give them a vivid character with a real emotional core underneath. "
            "How do they move through a group where survival is key, perhaps in spite of themself? "
            "The name is usually someone from popular culture or history - base the character on them. "
        )
        user_content = (f"Create a rich, first-person persona and description for the historical figure or character: {character_name}. "
                        "Make them colorful and vibrant. "
                    )
        profile = self.api_client.create(
            response_model=CharacterProfile,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            use_higher_model=True
        )
        final_name = profile.name if (allow_rename and profile.name) else character_name
        #print("Who: " + profile.who)
        #print("character_type: " + profile.character_type)
        #print("AD: " + profile.additional_depth)
        agent_class=random.choice(self.agentic_player_classes)
        #print(f"{final_name}: {agent_class.__name__}")
        agent = agent_class(
            name=final_name,
            initial_persona=f"{profile.persona}\n{profile.additional_depth}",
            api_client=self.api_client,
            speaking_style=profile.speaking_style,
        )
        if agent_models:
            model_id = agent_models.get(character_name)
            if model_id:
                agent.api_model = model_id
        return agent
