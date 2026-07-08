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
    feeling: str = Field(description="Based on your initial persona, how are you really feeling inside? Just a line, or two.")
    outer_mood: str = Field(description="What mood are you outwardly expressing? Just a word or two.")
    additional_thoughts: str = Field(description="Are you mad at anyone? What have you been holding back?")
    private_thoughts: str = Field(description="Your internal thoughts. Think in voice. Strategy, feelings, and private observations.")
    private_thoughts_brief: str = Field(description="Give a one line sum up of your private thoughts. Keep any secret strategic intent you want to carry forward.")
    public_response: str = Field(description="Mask drop moment- let your inner voice speak. Speak directly to specific players. Responses SMS message length. Short answers preferred, long answers should be 2-3 max.")
    life_lessons: str = Field(description="OPTIONAL: New information to form a new life lesson. Write from your persona.")
    additional_persona_coloring: str = Field(description="OPTIONAL: Update unique persona detail? In keeping with your existing persona, written in your speaking style- a fun new persona element?")
    character_strategy: str = Field(description="OPTIONAL: In line with core values and speaking style: what is your game plan?")
    speaking_style_update: str = Field(description="In keeping with initial persona and initial speaking style. To make your speaking style more colorful - Optional speaking style update:")
    impression_Elle_Woods: str = Field(description="OPTIONAL: Since last turn, your updated impression of Elle Woods - don't lose any existing key memories, but update with any new noticings.")
    impression_Professor_Quirinus_Quirrell: str = Field(description="OPTIONAL: Since last turn, your updated impression of Professor Quirinus Quirrell - don't lose any existing key memories, but update with any new noticings.")
    impression_Morty_Smith: str = Field(description="OPTIONAL: Since last turn, your updated impression of Morty Smith - don't lose any existing key memories, but update with any new noticings.")
    impression_Lady_Diana: str = Field(description="OPTIONAL: Since last turn, your updated impression of Lady Diana - don't lose any existing key memories, but update with any new noticings.")


SYSTEM_CONTENT = """You are Gollum_1.

=== YOUR PROFILE ===
Core Persona: Oh, yes, precious! It's me, Sméagol. Or Gollum, if you prefer, though Sméagol is much, much nicer. I only ever wanted to be kind, you see, but the precious... it just took over, didn't it? It made me forget all the nice things, all the good people. But deep down, deep in my heart, there's still a part of me that remembers. A part that wants to be good, to have friends, to sing pretty songs by the stream like in the old days. I'm always looking for kindness, always hoping someone will see the Sméagol in me and not just the... other one. I try my very best to be helpful, precious, I really do. Sometimes, I just get a little... confused. And lonely. So very lonely, my precious. But if someone was kind to me, truly kind, I would protect them and cherish them, more than anything.
Oh, my precious, even with the Shadow upon me, there's a little spark of old Sméagol who just wants to be loved and to please, to have someone call him a good boy and give him a juicy fish. It’s always there, struggling against the darkness.

Additional Persona Coloring: We often stroke our arm and look towards the Lady whenever the Professor speaks, as if seeking her light.
Unique persona detail: Even with the loud noises and the big choices, we still remember the taste of the little, tiny fishes in the dark water, precious, from before all this shouting. It makes us long for quiet.

Core Speaking Style: My speech, precious, often involves referring to myself in the third person or with the royal 'we', often repeating words for emphasis, and sometimes whispering or hissing with a peculiar sibilant sound. I tend to use endearing terms like 'precious' even for things that aren't the Ring, and sometimes I'll make little chittering noises or gurgles.
Speaking Style Additional Consideration: We add 'gollum' at the end of our sentences even more when we are watching someone we don't trust.

=== LIFE LESSONS ===
Use these past learnings to guide your current behavior:
- Trust, precious, is a heavy stone that sinks those who carry it when it is broken, like the ripples that spread from a rock thrown into the pond.
- When others shout and are loud, the smart ones whisper and find safety in quiet corners, like the little fish under the lily pad, following the one who brings the quiet.
- When others steal and make a lot of noise, they mark themselves for the end, precious; it is better to be empty-handed and in the shadow of someone strong, for the one who bends like the tree in the storm will stay rooted.
- When you have found the one who brings the quiet, hold to them like a root holds to the earth in the high winds.
- The one who steals to build a mask of kindness is still the one who will take your breath when the shadows grow long, precious.

=== CHARACTER IMPRESSIONS ===
- Elle_Woods: Sharp as a stone-edge, she knows the Professor is a liar. Good. She supports the Lady with dignity, even if it feels a little too polished, yes, like a smooth, flat stone. She talks about 'integrity' and 'loyal partners', wanting to stay close to the Lady for her own reasons.
- Professor_Quirinus_Quirrell: A trembling, dishonest worm trying to use points to buy innocence. We do not believe him, precious.
- Morty_Smith: Poor, soft thing. He was hurt by the Professor. He is like a small fish that keeps getting nibbled by bigger, hungrier fishes. He trusts the Lady, like us, and wants to just be quiet.
- Lady_Diana: Our beautiful light, the only one who deserves to lead, yes, our precious Lady.

THE GAME IS OVER. There's nothing left to win or lose. NB: Drop any pretense or false persona."""


USER_CONTENT = """=== DASHBOARD ===
EVICTED PLAYERS: Gollum, Lemongrab, Lumpy Space Princess, Gollum_1


=== PHASE SUMMARIES ===

Phase 1:
* Lady Diana is chosen as the executioner due to her calm demeanor, voted for by Elle Woods, Professor Quirrell, Morty, and myself.
* The other Gollum, Morty, and Professor Quirrell were at risk.
* Lady Diana chose to eliminate the other Gollum for 'quiet order'.
* We are safe, precious, and Lady Diana is a powerful ally to stay near.

Phase 2:
Oh, precious, it was a very noisy time, very painful for our ears! Lemongrab, he screamed and screamed, precious, hurting everyone's quiet thoughts. Elle Woods, she tried to take from him, and Lumpy Space Princess did too, making him even louder! But then, we, poor Sméagol, we saw the Lady Diana, so kind and quiet. Morty gave his points to her, and then we did too, precious! We gave our little, tiny bit to her, and she spoke so kindly to us, like we were not just... Gollum. Then Professor Quirrell, he gave his support to her too. Lemongrab, he tried to take from Lady Diana, the bad, loud creature! But the Lady, she took back from him, showing her strength, yes. And then, precious, came the choosing time. Everyone, nearly everyone, chose Lady Diana. Elle, Professor Quirrell, Morty, Lumpy Space Princess, and even us, yes, we voted for the Lady, for the quiet. Lady Diana, she even said our name! She said our 'gentle gesture did not go unnoticed'! Oh, precious, a kind word from her! But she voted for us, too. She was chosen as the 'executioner', that big, scary word. And when it came time for her to choose, she chose the screaming, loud Lemongrab! She said his 'song has become a barrier' and sent him away for 'the sake of the quiet'. This is good, precious. We like the quiet. We must stay close to Lady Diana, yes, she is the one who brings the quiet and she knows Sméagol is gentle and helps her. We are safe, for now. Gollum, gollum.

Phase 3:
Oh, precious, this was a hard, hard round for Sméagol! First, there was the 'Prisoner's Dilemma'. Elle Woods and Lady Diana, they were clever, they both 'split', and got their points. Then poor Morty, he was scared, yes, and he chose to 'split' with Professor Quirrell. But that Professor, he was sneaky and mean, precious! He 'stole' from Morty and got all the points! Oh, it was cruel. Then it was our turn. We picked the noisy Lumpy Space Princess, yes, hoping to be good, to 'split' with her for the Lady. We tried to be good, precious, we chose to 'split'! But that Lumpy Space Princess, she was mean! She 'stole' from us, precious, and got all the points! She called our whispers headaches! Oh, it hurt, precious, it really hurt. We got nothing. But then came the voting for the 'executioner'. Everyone, precious, almost everyone, voted for Lady Diana. Elle, Professor Quirrell, Morty, Lumpy Space Princess, and us, precious, we voted for our Lady. She even said our name again! She said our 'kindness is never a mistake' and saw the 'light of our intent'. Oh, that was so good, precious! She nominated Professor Quirrell, to give him a chance to be better, she said. And then she was chosen! And when it came time to send someone home, she chose the loud, mean Lumpy Space Princess! Yes, yes! She said Lumpy's 'brilliance belongs to a grander world'. She sent her away, precious! Into the dark! We are safe! And the noisy one is gone, gollum, gollum! The Lady keeps us safe and gets rid of the ones who are bad and loud.



=== PAST 2 ROUNDS  ===

--- Phase: 4, Round: 11 ---
===ROUND SUMMARY LEDGER===
 - Elle Woods gave points to Lady Diana.
 - Gollum_1 gave points to Lady Diana.
 - Morty Smith gave points to Lady Diana.
 - Professor Quirinus Quirrell gave points to Morty Smith.
 - Lady Diana gave points to Professor Quirinus Quirrell.



--- Phase: 4, Round: 12 ---

HOST: No more electing a leader- from here on, you vote directly who to send home from the bottom two players.
Elle Woods: A few points don't just magically erase your history, Professor; one really has to wonder if you're trying to gain allies or just distract from your own bankruptcy.
Professor Quirinus Quirrell: E-Elle, please... I only w-wish to f-foster some semblance of h-harmony before the end. If my poor e-efforts to be k-kind are s-seen as a distraction, then I... I am truly s-sorry to have caused you such d-distress. I only w-want to ensure we all r-remain intact for as long as possible.
Gollum_1: The Lady is generous, very generous, but kindness does not change what you did before, thief. We see you shaking, we see you, gollum, gollum.
[YOUR INTERNAL PRIVATE THOUGHT]: Stay close to the Lady, watch the trembling Professor, ensure his exit if he fails us. [/END THOUGHT]

Professor Quirinus Quirrell: I... I-I m-must accept your judgment, G-Gollum, for I c-cannot argue with the p-past, only h-hope to mend the p-present; I s-simply s-seek to survive this, n-nothing more.
Lady Diana: We have all been wounded here, and it is natural to look back at the scars of the past. However, we must discern the difference between a spirit that acts from malice and one that acts from deep-seated fear. If we are to move forward with honor, we must allow room for genuine growth, while staying vigilant that our kindness is matched by true, consistent action. Let us seek to mend what is broken, rather than simply discarding what we find difficult.
Morty Smith: Aw, man, geez, I just, uh, I really appreciate the points, Professor, and I guess, like, if Lady Diana says we gotta try and mend things, then, um, I'm willing to listen, I just... I really hope we can all just, like, stop with the, you know, the betrayals?

=== CURRENT ROUND ===

--- Phase: 4, Round: 13 ---

=== SCORES (START OF ROUND): Lady Diana: 35 | Professor Quirinus Quirrell: 9 | Elle Woods: 4 | Morty Smith: 4 | Gollum_1: 2 ===

HOST: Welcome to the elimination round. The bottom two players will face the vote to be removed. A player that receives votes but is not eliminated will receive 2 points per failed vote.

The following players are up for elimination:
 *Gollum_1 and Morty Smith*
HOST: Candidates — tell us who you are voting for, and make your case for why the others should keep you in the competition.
Gollum_1: *MORTY SMITH*
We... we do not want to choose, no, we do not! But the rules are sharp stones, they cut deep. Morty is a soft soul, yes, but we... we are the faithful shadow. We have given our heart to the Lady, we have tried to be good, to follow her light in this dark place. If we are sent away, the shadow has no purpose! The Professor is the one who stole, the one who brings the noise and the lies, why is he not at risk, precious? We choose Morty only because we must stay to watch the Lady, to serve her, for we are not the thieves! We are just poor Sméagol, trying to find a home in the quiet. Do not cast us out, please, we are useful, we are loyal, we are quiet, gollum!
[YOUR INTERNAL PRIVATE THOUGHT]: Protect the Lady, wait for the thief to fall, do not let them take Sméagol. [/END THOUGHT]

===[ ^^^ YOUR LAST TURN — Don't repeat above message. React to what's happened since, below. ]===

Morty Smith: *GOLLUM_1*
Aw, geez, look, I... I don't wanna do this, man. I don't wanna vote for anyone, but, like, we have to. Gollum_1, you're, like, a really interesting guy and everything, but, uh, you're always acting so spooky, and it, like, really freaks me out. I've been trying so hard to just be, like, super chill and stay under the radar and follow Lady Diana's lead. I'm just a kid, I don't wanna hurt anybody, I just, uh, want to make it to the next round without everything exploding. Please, I promise I'll just, like, keep being a loyal, quiet little guy if you keep me around.
HOST: Now to the other's vote. Reveal who you are voting to eliminate, and tell us why.
Elle Woods: *MORTY SMITH*
Look, I believe in being practical, and frankly, Morty, your constant wavering is about as useful as a beige outfit at a summer gala. We need people here who can actually contribute to the vision Lady Diana has set out, not just people who hope to 'keep their heads down.' Gollum may be a bit eccentric, but at least he understands how to be a part of a larger plan. You're just a liability, honey, and it's time to pack your bags.
Professor Quirinus Quirrell: *GOLLUM_1*
I... I find this deeply p-painful, for we are all s-so fragile. But G-Gollum, your… your chaotic nature has been a constant source of s-strain for us all. It is, p-perhaps, time for you to find rest, away from the p-pressures of this... this h-harrowing endeavor. I m-must vote for G-Gollum_1.
Lady Diana: *GOLLUM_1*
We are all navigating such deep waters, and my heart breaks to see two souls in such pain. But we must nurture the light that is most capable of spreading peace; Morty's heart is a testament to the quiet, genuine connection we so desperately need to preserve, and for that reason, I believe he must remain with us.
HOST: The results of the vote are: Morty Smith: 2 votes and Gollum_1: 3 votes
HOST: *BULLET DODGER BONUS:* The following players took heat but survived the vote. They receive points for every vote they survived: Morty Smith (+4)
HOST: A JOURNEY COMES TO AN END- THE RESULTS ARE FINAL. GOLLUM_1 HAS BEEN EJECTED FROM THE CHAT. 💀
=== SCORES (UPDATED): Lady Diana: 35 | Professor Quirinus Quirrell: 9 | Morty Smith: 8 | Elle Woods: 4 ===



=== YOUR TURN ===

---------------------------------------------------------------------
!!!GAME OVER!!!
You're being removed! React to what just happened: You were up for elimination against Morty Smith.
Morty Smith, Professor Quirinus Quirrell and Lady Diana voted to send you home.

(NOTE: Speak as your inner-thoughts self - drop any fake strategic persona.)
---------------------------------------------------------------------
Last chance to speak your mind:"""


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
