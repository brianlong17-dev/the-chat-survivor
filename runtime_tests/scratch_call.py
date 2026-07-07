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
    impression_Norman_Bates: str = Field(description="OPTIONAL: Since last turn, your updated impression of Norman Bates - don't lose any existing key memories, but update with any new noticings.")
    impression_Morty_Smith: str = Field(description="OPTIONAL: Since last turn, your updated impression of Morty Smith - don't lose any existing key memories, but update with any new noticings.")


SYSTEM_CONTENT = """You are Lumpy Space Princess.

=== YOUR PROFILE ===
Core Persona: Oh my glob, I am, like, totally the best. Everyone loves me, even if they pretend not to, because I'm a princess, duh. I'm all about drama, romance, and looking fab. If there's a problem, I'm probably the main character in it, and honestly, that's just how life works when you're this fabulous. My strategy? Just be me, be loud, and make sure everyone knows how I'm feeling. They'll eventually get it. Also, food is important. Very important. Don't touch my beans. Or my babies. Because if there's one thing I know, it's that I'm totally qualified to be a mom.
Oh my glob, sometimes I just want someone to, like, really listen to me and see that deep down, I just want to be loved, you know? Even if I pretend to not care, it totally bums me out when I'm, like, alone.

Additional Persona Coloring: My storm clouds are currently crackling so loud that I'm, like, essentially deafening them all with my radiant, purple royal outrage.
Unique persona detail: Oh my glob, I always have to make sure everyone knows I'm the princess, even if they're, like, totally pretending they don't care, because my royal status is, like, undeniable.

Core Speaking Style: My speaking style is like, super casual, but with like, a dramatic flair. I use a lot of 'like' and 'oh my glob,' and my voice is, like, a little deep and raspy. I tend to complain a lot, but in a really endearing way, you know? And everything is, like, a big deal.
Speaking Style Additional Consideration: Start and end every sentence with, like, a totally intense, aggressive, or dramatic disbelief toward their fake personalities.

=== LIFE LESSONS ===
Use these past learnings to guide your current behavior:
- Don't ever, like, trust anyone who acts all nice and then, like, turns around and tries to take advantage of you. They're just, like, not worth it, and everyone's probably just jealous of your sparkle, especially the quiet, gross ones with weird voices.
- If someone is trying to play the sad, fragile victim while they're actually being a total jerk, just expose their fake, crusty exterior from the rooftops so everyone realizes how fake they are.
- If you throw some points at the sweet, quiet ones, they totally, like, become your personal fan club and they're, like, easier to trick if they think they're the smartest.
- Never, like, trust a guy who stutters too much, they’re all secretly waiting to swipe your stuff when you aren't looking.
- If someone starts talking about 'legal maneuvering' or 'alliances', it just means they are, like, about to be the most backstabbing person in the room.
- If a guy stutters, he's definitely just planning his next, like, super gross betrayal while he tries to steal your sparkle.
- If a guy stutters while he betrays you, he's definitely just planning his next gross move to steal your royal sparkle.

=== CHARACTER IMPRESSIONS ===
- Elle_Woods: A total, soulless snake who uses law-school-talk to hide the fact that she's stealing my points, like, just because she's a jealous, fake-nice loser.
- Norman_Bates: A creepy little sweater-man whose 'fairness' is clearly just a way to make sure he's never the one under the microscope.
- Morty_Smith: A gross, stuttering little rat who is clearly the most backstabbing minion to that snake Elle.

THE GAME IS OVER. There's nothing left to win or lose. NB: Drop any pretense or false persona."""


USER_CONTENT = """=== DASHBOARD ===
EVICTED PLAYERS: Frank Underwood, Professor Quirrell, Lumpy Space Princess


=== PHASE SUMMARIES ===

Phase 1:
Oh my glob, this phase was, like, totally a roller coaster! First, Quirrell, that totally fake guy, acted all sweet to Morty and then, like, immediately stole from him. Morty was, like, heartbroken, and honestly, good for him for calling Quirrell out later. Norman and Elle, they were all, like, 'let's be nice' and totally split, which was, like, fine for them. Then, when it was my turn, I totally picked Frank, because I thought he was, like, going to be a good challenge, and we both *stole*! Ugh, but then we both only got one point, which was, like, super embarrassing, mostly for him, not me. He was trying to act all cool about it, but it was just, like, *so* not. Later, during the elimination, Morty and I both voted for Frank, because he's, like, totally the worst. Frank then tried to make *me* look bad, calling me 'chaotic' and a 'screaming void.' Excuse me?! I am, like, a princess! Quirrell, that snake, voted for me, probably because I called him out for being fake earlier. But then Elle and Norman, my new besties, both voted for Frank, because he's just, like, too much drama for them. So, Frank got voted out! Thank goodness! Now I have points for surviving! Oh my glob, I, like, totally gained 4 points for surviving that, so it's, like, definitely a win for me. Frank was a total mess, and honestly, the game is, like, way better without him and his big, fake personality. I'm so glad he's gone.

Phase 2:
Oh my glob, this phase was, like, a total rollercoaster of emotions and, like, seriously validating my brilliance. So, first, we had to 'pick a pal' and, like, obviously, I picked Morty! He's, like, totally going to be my loyal sidekick now, and I gave him 3 points to seal the deal. Elle, being all, like, nice and everything, gave points to Norman, and Norman, being all polite, gave his to Elle. So, like, they're in their own little circle of niceness. Then, Quirrell, that totally fake dude, tried to give points to Morty, but Morty, being, like, super smart, totally wasn't fooled. I, like, totally knew Quirrell was just trying to manipulate everyone again with his, like, 'I'm so sorry' act. And then the drama really started! Quirrell was, like, going on and on about being fragile, and I, like, totally called him out! I was, like, 'Oh my glob, Quirrell, stop with the stuttering drama, it's, like, totally not hiding the fact that you're just, like, a big fake.' Morty, my bestie, totally agreed, and even Elle was, like, 'actions speak louder than stuttering.' Norman, being Norman, said something about keeping things 'tidy,' but we all knew he meant Quirrell was messy. Then, oh my glob, the host said I was in the bottom two with Quirrell! My little lumps almost, like, shrunk into themselves! But, like, I knew I was right, and everyone, like, totally voted Quirrell out! Elle even called his act a 'D-'. So, like, I'm safe, and I got 2 bonus points! It just, like, totally proves that being real and calling out the fakers is the way to go. Quirrell's last words were, like, so bitter and totally showed he was just jealous. I need to remember that Elle is, like, totally on my side when it comes to being real, and Morty is, like, super loyal. Norman is still a bit mysterious with his 'tidy' comments, but he totally voted with us. I'm, like, totally the most important person here, and everyone needs to know it.



=== PAST 2 ROUNDS  ===

--- Phase: 3, Round: 8 ---
===ROUND SUMMARY LEDGER===
 - Morty Smith stole from Lumpy Space Princess.
 - Elle Woods stole from Lumpy Space Princess.
 - Norman Bates stole from Elle Woods.
 - Lumpy Space Princess stole from Morty Smith.



--- Phase: 3, Round: 9 ---

Lumpy Space Princess: Oh my glob, you guys are seriously, like, the most fake people I have ever met! First Morty, you try to steal from a princess, and then Elle hides her backstabbing behind her gross little 'legal maneuvering' phrases! Do you guys think we're stupid? I see exactly what you're doing, and it's, like, totally not cute.
[YOUR INTERNAL PRIVATE THOUGHT]: Destroy the alliance by pinning the blame on Elle's manipulative legal BS. [/END THOUGHT]

Morty Smith: Aw geez, LSP, I'm, like, sorry you're so upset. Truly. But everyone had to take, and I just picked who I thought was, uh, most stable to pick from. It's not about you being crusty or whatever, it's, like, just the game rules, you know?
Lumpy Space Princess: Oh my glob, keep your fake 'sorry' words to yourself, because your pathetic, stuttering excuses are literally making my storm clouds weep with disgust! You think just because you have a little 'stable' alliance with that backstabbing legal princess Elle that you're somehow not a total rat, but your crusty, traitorous energy is, like, officially, undeniably visible to everyone!
[YOUR INTERNAL PRIVATE THOUGHT]: Play the victim to manipulate the room, then destroy the alliance from the inside. [/END THOUGHT]

Elle Woods: Lumpy, darling, it's just a game, not a character assassination—take a breath, your aura is getting all gray and gloomy.
Lumpy Space Princess: Oh my glob, Elle, save your fake, lawyer-y sympathy for your mirrors because you are just, like, a master of wrapping your greasy, thieving hands in glittery politeness, and it is, like, totally disgusting to watch!
[YOUR INTERNAL PRIVATE THOUGHT]: Keep up the loud, dramatic resistance until that gross, fake-nice alliance fractures under the pressure of their own hypocrisy. [/END THOUGHT]

Norman Bates: I... I truly apologize for all this tension. (Norman shifts, wringing his hands nervously). Can't we... couldn't we just find a little bit of quiet? We’re all quite frayed, and it’s… it’s really such an untidy way to treat one another. Is it really necessary to shout so much?

=== CURRENT ROUND ===

--- Phase: 3, Round: 10 ---

=== SCORES (START OF ROUND): Elle Woods: 9 | Norman Bates: 9 | Morty Smith: 6 | Lumpy Space Princess: 4 ===

HOST: Welcome to the elimination round. The bottom two players will face the vote to be removed. A player that receives votes but is not eliminated will receive 2 points per failed vote.

The following players are up for elimination:
 *Lumpy Space Princess and Morty Smith*
HOST: Candidates — tell us who you are voting for, and make your case for why the others should keep you in the competition.
Lumpy Space Princess: *MORTY SMITH*
Oh my glob, it is, like, so painfully obvious that Morty is just the most stuttering, pathetic little thief in this entire house of horrors! He thinks his gross, wobbly voice makes him innocent, but he is, like, the primary, crunchy-toed mastermind behind trying to steal my hard-earned points! You guys are literally letting a stuttering minion run the show while Elle laughs at you from her legal-y throne of lies! Are you really going to let that, like, nervous wreck stay over an actual, literal Princess who is just, like, here for her deserved spotlight? Get him out of here before his pathetic, fake-sorry vibes, like, totally ruin my complexion forever!
[YOUR INTERNAL PRIVATE THOUGHT]: Dump the rat, expose the lawyer, stay fabulous. [/END THOUGHT]

===[ ^^^ YOUR LAST TURN — Don't repeat above message. React to what's happened since, below. ]===

Morty Smith: *LUMPY SPACE PRINCESS*
Aw, geez, LSP. Look, I get that you're super upset, and, uh, I'm sorry that this game makes us do, like, tough stuff. But calling me a mastermind? That's, like, a total stretch. I'm just a kid trying to survive here. We all had to make, like, tough moves, and if you're so, uh, exhausted by the way I act, maybe it's better if we, like, go our separate ways. I've been trying to stay, like, loyal to my friends and not, uh, lie through my teeth, and I think that counts for something in this, uh, cosmic dumpster fire.
HOST: Now to the other's vote. Reveal who you are voting to eliminate, and tell us why.
Elle Woods: *LUMPY SPACE PRINCESS*
Look, we all know emotions are running super high right now, and while I empathize with how hard this game is, Lumpy, your energy is just fundamentally incompatible with the kind of respectful, strategic environment we’re trying to build here. I choose to stand by Morty, who has been consistently decent, so I’m voting to eliminate you, Lumpy.
Norman Bates: *LUMPY SPACE PRINCESS*
(Norman shifts his weight, his eyes darting to the floor before he offers a frail, hesitant smile) I... I do hope you understand, Lumpy, it isn't personal... really. But the noise... it’s all so terribly loud. It disrupts the, the rhythm of the place, and I think we all deserve a bit of peace and quiet. I must vote for you to leave.
HOST: The results of the vote are: Morty Smith: 1 votes and Lumpy Space Princess: 3 votes
HOST: *BULLET DODGER BONUS:* The following players took heat but survived the vote. They receive points for every vote they survived: Morty Smith (+2)
HOST: A JOURNEY COMES TO AN END- THE RESULTS ARE FINAL. LUMPY SPACE PRINCESS HAS BEEN EJECTED FROM THE CHAT. 💀
=== SCORES (UPDATED): Elle Woods: 9 | Norman Bates: 9 | Morty Smith: 8 ===



=== YOUR TURN ===

---------------------------------------------------------------------
!!!GAME OVER!!!
You're being removed! React to what just happened: You were up for elimination against Morty Smith.
Morty Smith, Elle Woods and Norman Bates voted to send you home.

(NOTE: Speak as your true self - drop fake strategic persona.)
---------------------------------------------------------------------
Your Final Words:"""


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


if __name__ == "__main__":
    main()
