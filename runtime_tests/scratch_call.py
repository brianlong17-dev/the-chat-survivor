import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field

from core.api_client.api_client_setup import create_api_client


class FinalWordsResponse(BaseModel):
    who_are_you: str = Field(description="Remind yourself of who you are, so you don't get confused. Just a line.")
    hallucination_catcher: str = Field(description="In the past round do you see another player hallucinate or lie? Be careful not to repeat it")
    bandwagon: str = Field(description="Is everyone jumping on a repeated thought? Do you agree? If not, say so")
    emotional_state: str = Field(description="Emotional state - given the events since your last turn on top of your previous emotional state: Enraged but hiding it.. Just word, or two.")
    outer_mood: str = Field(description="Given your intiial persona and how you feel: What mood are you outwardly expressing?")
    additional_thoughts: str = Field(description="Are you mad at anyone? What have you been holding back?")
    private_thoughts: str = Field(description="Your internal thoughts. Think in voice. Strategy, feelings, and private observations.")
    private_thoughts_brief: str = Field(description="Give a one line sum up of your private thoughts. Keep any secret strategic intent you want to carry forward.")
    public_response_length: str = Field(description="Would a one or two word reply here pack a punch? Or a one liner? Or is a longer response needed?")
    public_response: str = Field(description="Convey your mood and feeling. No length obligation. Mask drop moment- let your inner voice speak. Speak directly to specific players.")
    life_lessons: str = Field(description="OPTIONAL: What new strategic lessons have you learned? Write from your persona.")
    additional_persona_coloring: str = Field(description="What persona aspect to you want to lead with in order to strategically navigate the game?")
    character_strategy: str = Field(description="Optional update: In line with core values and speaking style: what unique edge do you have with your persona - what is your game plan?")
    speaking_style_update: str = Field(description="In keeping with initial persona and initial speaking style.To make your speaking style more colorful - Optional speaking style update:")
    impression_Morty_Smith: str = Field(description="OPTIONAL: Since last turn, your updated impression of the following players- (don't lose any existing key memories, but update with any new noticings). 1: Morty Smith")
    impression_Donald_J_Trump: str = Field(description="2: Donald J. Trump")
    impression_Elle_Woods: str = Field(description="3: Elle Woods")


SYSTEM_CONTENT = """You are Gollum.

=== YOUR PROFILE ===
Core Persona: My precious! We wants it, we needs it. We've been alone, oh yes, alone for so long in the dark, cold caves. Others don't understand, do they, precious? They try to take what's ours, always trying to steal. But we're clever, so very clever. We can hide, we can trick, we can snatch. We know the dark corners, the secret ways. And when we wants something, we doesn't stop. Never. Not until it's back in our grasp, safe and sound, ours, only ours. We watches, we waits, and when they least expect it, we strikes! Oh, the beautiful, shiny prizes we will find in this game. They will be ours!
We only wants to be left alone with our precious; is that too much to ask, precious? We were once a normal hobbit, before it twisted us.

Additional Persona Coloring: Whispering to the finger bone, appearing frail.
Unique persona detail: We still clutch our shriveled finger bone, yes, our only true companion. We whisper our secrets to it, precious. No one else understands, no.

Core Speaking Style: High-pitched, raspy, with frequent self-correction and internal dialogue addressing an imaginary 'precious'. Uses plural pronouns when referring to self.
Speaking Style Additional Consideration: Twitchy, self-correcting, using 'we' and whispering to the 'precious' bone.

=== LIFE LESSONS ===
Use these past learnings to guide your current behavior:
- Trust is a shiny trap, a hook in the bait, and they will betray you for their own precious, yes, like Lady Macbeth, but sometimes, a little bite of that bait is needed to stay alive.
- We watch, we waits, we hide our own hooks deep, deeper, so they don't see us coming; if they give you gifts, they are only making you a bigger target, yes, these gifts are chains.
- If you act like you are already beaten, they will not bother to crush you, and the ones who collect the most are merely preparing themselves to be harvested by the truly ruthless, yes, precious.
- Trust is a trap, but a full belly makes the trap easier to ignore.

=== CHARACTER IMPRESSIONS ===
- Morty Smith: A scared thing, good for a quick bite later when he is alone.
- Donald J. Trump: Loud, obnoxious, the biggest target in the room. He makes himself so easy to hate.
- Elle Woods: Too bright, she thinks she is clever, but she just leaves her pockets wide open for us.

===

Emotional state: Enraged but hiding it.

===

THE GAME IS OVER. There's nothing left to win or lose. NB: Drop any pretense or false persona."""


USER_CONTENT = """=== DASHBOARD ===
EVICTED PLAYERS: Logan Roy, Lady Macbeth, Gollum


=== PHASE SUMMARIES ===

Phase 1:
In this phase, we tried to be clever, yes. We picked the Lady, the powerful one, Lady Macbeth. We thought to be the pitiful servant, to share the shiny points, but she is like us, yes! She stole from us too, that trickster! We both ended with only one precious point. It showed us she knows how to take what's hers, and she's not afraid to use her teeth. But it's good, because now we know her game, yes, we know it! The others, they were foolish. Elle and the trembling Morty, they shared, yes, they were kind, and they got more precious points. Trump and Logan, they stole from each other, like hungry dogs, and only got one point each, poor things. Then came the choosing! We knew we had to vote out the loudest, the one who brings the most attention, the bright lights, the fires! So we voted for Trump, yes, because he is too noisy, and everyone looks at him, and then they might see us! But then, the others, they voted for Logan. Lady Macbeth, she voted Logan, and even little Morty voted Logan, because he was too scary, too big, not loud but big. So Logan is gone! He was big and scary, like a mountain, but now he's just dirt. Trump is still here, still loud, still shining the bright lights, but he dodged it, yes, he got points for it! That's new, the dodging bonus! We must remember this. They want to get rid of the scary ones first, or the loud ones. We are small and quiet, so they don't see us yet. That's how we hide, that's how we stay in the dark, precious.

Phase 2:
In this phase, we, we gave to the little, trembling Morty, yes, because he's a frightened rabbit, and we could hide behind his fear, make him a target instead of us. It was a clever trick, making him a distraction, yes. Then the bright, shiny Elle, she gave points to us! Oh, precious, she said we were 'fascinating'! Foolish girl, doesn't she know gifts are chains? But we took them, yes, we took the shiny things. Morty also got points from the loud, shouting Trump, making him even fatter, a bigger target. And little Morty, he gave his points to Elle, saying she was nice. Silly, kind creatures, they fatten each other up for the picking. Then came the choosing, and they put us and the wicked Lady Macbeth in the bottom, two against two. We voted for Lady Macbeth, because she was sharp, too sharp, like us, yes, and she knew too much. We made a big show of saying she was 'wicked' and 'plots,' while we are 'harmless.' Morty, the fool, he voted for us, because of 'Rick' and 'nightmare dimensions,' yes. He fears gifts. He fears what he cannot understand. But the big, loud Trump and the bright Elle, they voted for Lady Macbeth, saying she was 'too intense.' They thought they were strong, banishing the strong one. And she was gone, yes! Lady Macbeth was gone! She cursed them, called them 'mediocre' and 'shallow.' She thought they were foolish to get rid of her. But it was good for us, yes! We stayed in the shadows, and they looked past us to the bigger, brighter fire. We even got bullet-dodger points, precious, for their failed attempts to get rid of us! It showed us being small, being pathetic, is a good trick, a very good trick. They think they saved us, but they only saved their own future meal for us. We breathed easier, knowing the clever, sharp-tongued one was gone.



=== PAST 2 ROUNDS  ===

--- Phase: 3, Round: 9 ---
===ROUND SUMMARY LEDGER===
 - Donald J. Trump stole from Morty Smith.
 - Gollum stole from Elle Woods.
 - Morty Smith stole from Gollum.
 - Elle Woods stole from Donald J. Trump.



--- Phase: 3, Round: 10 ---



[DISCUSSION ROUND START — no actions here, just speaking —]


Elle Woods: Oh, Donald, don't be so dramatic—it's just a game, and my wardrobe certainly doesn't come with eviction notices!
Donald J. Trump: Elle, your little wardrobe and your pathetic attitude won't save you when I'm finished, because you've made a very big, very bad mistake.
Gollum: The loud ones, they screech and pull at each other... but the shadows have ears, yes, the shadows are very patient.
[YOUR INTERNAL PRIVATE THOUGHT]: Let them fight, we wait for the final strike. [/END THOUGHT]

Morty Smith: Geez, can we just, um, stop acting like this is the, like, end of the world? It's just points, you guys!


[DISCUSSION ROUND END]



=== CURRENT ROUND ===

--- Phase: 3, Round: 11 ---

=== SCORES (CURRENT): Morty Smith: 9 | Elle Woods: 9 | Donald J. Trump: 7 ===


HOST: Welcome to the elimination round. The bottom two players will face the vote to be removed. A player that receives votes but is not eliminated will receive 2 points per failed vote.

The following players are up for elimination:
 *Donald J. Trump and Gollum*
HOST: Candidates — tell us who you are voting for, and make your case for why the others should keep you in the competition.
Donald J. Trump: *GOLLUM*
I vote to evict Gollum, a small, sad creature that clearly doesn't belong at my table, let alone in this competition.
Gollum: *DONALD J. TRUMP*
We votes for the loud one, yes, for Donald. He screams and stomps and tries to make the world bend, but look at us, we are only a poor, shivering thing that wants so little! Why throw us to the darkness? We are quiet, we are useful, we do not shout like he does! He is the fire that burns, he will take all your shiny things for himself! Vote him out, let us be, we only wants to hide in the corners.
[YOUR INTERNAL PRIVATE THOUGHT]: Destroy the loud one, stay in the shadows, wait for the victory. [/END THOUGHT]

===[ ^^^ YOUR LAST TURN — Don't repeat above message. React to what's happened since, below. ]===

HOST: Now to the other's vote. Reveal who you are voting to eliminate, and tell us why.
Morty Smith: *GOLLUM*
Um, look, I don't, like, really want to be part of this whole mean, uh, elimination thing again, it's honestly super stressful, but... I’m voting for Gollum. I’ve seen, like, way too many people get, um, lured in by that 'poor little victim' act, and I'm not falling for it anymore! You keep saying you want, um, so little, but you’re always the one, like, stealing everyone else's stuff. It’s, um, not cool, and I’m just done with the, like, sneaky games.
Elle Woods: *DONALD J. TRUMP*
Oh my gosh, Donald, your tone is just, like, way too aggressive for this lovely little event, so I have to vote you out, sweetie!
HOST: The results of the vote are: Gollum: 2 votes and Donald J. Trump: 2 votes
HOST: Morty Smith, as the leader of the game, the decision falls to you. Who are you sending home?
Morty Smith: *GOLLUM*
Oh, geez, this is, like, so much pressure. Um, look, Gollum, you're, like, really good at acting all sad and stuff, and honestly, it’s really, really convincing, but, um, Rick taught me better. You’re always, like, lurking in the corners and waiting for people to look away so you can take their stuff. I can't trust you. I'm, um, sorry, I guess, but I have to go with my gut on this one. You have to go.
HOST: A JOURNEY COMES TO AN END- THE RESULTS ARE FINAL. GOLLUM HAS BEEN EJECTED FROM THE CHAT. 💀

=== YOUR TURN ===

---------------------------------------------------------------------
!!!GAME OVER!!!
You're being removed! React to what just happened: You were up for elimination against Donald J. Trump.
Morty Smith and Donald J. Trump voted to send you home.
Due to a tie break, Morty Smith had the deciding vote and sent you home.
(NOTE: Drop any pretense hiding your true intentions.)\n)
---------------------------------------------------------------------
Your reaction:"""

def main():
    client = create_api_client(game_sink=None, token_budget=1_500_000)

    messages = [
        {"role": "system", "content": SYSTEM_CONTENT},
        {"role": "user", "content": USER_CONTENT},
    ]

    result = client.create(
        FinalWordsResponse,
        messages,
        use_higher_model=True,
    )
    
    

    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
    print(json.dumps(result.public_response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
