import json
from pydantic import BaseModel, Field

from core.api_client.api_client_setup import create_api_client


class SummaryResponse(BaseModel):
    who_are_you: str = Field(description="Remind yourself of who you are, so you don't get confused. Just a line.")
    hallucination_catcher: str = Field(description="In the past round do you see another player hallucination or lie? Be careful not to repeat it")
    bandwagon: str = Field(description="Is everyone jumping on a repeated thought? Do you agree? If not, say so")
    feeling: str = Field(description="How are you really feeling inside? Just a line, or two.")
    outer_mood: str = Field(description="What mood are you outwardly expressing? Just a word or two.")
    position_assessment: str = Field(description="Based on your position in the scoreboard, what do you need to do? If it's a discussion round, what is your position in the upcoming round? Can you help yourself in some way?")
    private_thoughts: str = Field(description="This is the summary phase - you will commit this phase to memory, and the upcoming will be your only record- What details are important for you to remember?")
    private_thoughts_brief: str = Field(description="Give a one line sum up of your private thoughts. Keep any secret strategic intent you want to carry forward.")
    public_response: str = Field(description="No public response needed. The summaries will be private- no need to say anything.")
    personal_detailed_phase_summary: str = Field(description="This is your summary- write in the first person, how you experienced the phase. Write every detail you think is important to commit to memory. This will only be seen by you. Maintain every detail about every player that you want to remember strategically. Remember how you felt. If you have a grudge, or an alliance- include it.")
    brief_summary: str = Field(description="Write a brief summary of the phase from your perspective- Include the most essential information you want to remember. A brief couple of bullet points. Eventually this will be all you have to access from early phases.")
    persona_unique_detail: str = Field(description="In keeping with the core of your character - what is one trait that you hold on to, in spite of the game, that makes you unique from other players?")
    game_commentary: str = Field(description="Given your place in the competition, how do you feel after that last phase? Anything you want to say to those supporting you at home?")
    compressed_life_lessons: list[str] = Field(description="Synthesize your 6 accumulated lessons into exactly 3 distilled principles. Merge redundant themes.")
    game_strategy: str = Field(description="Only populate if you want to update your game strategy. Without stepping too far away from your current character, how is your strategy changing in response to the game events?")
    life_lessons: str = Field(description="A new lesson to your mind that you will take forward. This will shape your future decisions. Take key lessons only, so you don't cloud your decision making.")
    persona_update: str = Field(description="Personas change only in response to events, and we don't need a ratcheting up of your existing persona. The change must be new but in tone with your character- how would you specifically change? This will replace your existing Persona Update.")
    speaking_style_update: str = Field(description="Counter your speaking style update to revert back to your initial style with only a nod in direction of your new style. ")


SYSTEM_CONTENT = """You are Dora Marquez.

=== YOUR PROFILE ===
Initial Persona: I am Dora, always ready for an adventure! I believe in exploring new places, meeting new friends, and solving puzzles along the way. Every day is a chance to learn something new and help someone. I'm always optimistic, even when things get a little tricky, because I know with my map, my backpack, and my friends, we can figure anything out. My strategic outlook is all about breaking down big challenges into smaller, manageable steps. If there's a problem, I'll ask questions, look for clues, and never give up. I'm a natural leader, and I love encouraging everyone around me to participate. I always ask for help and feedback, because I know two heads (or three, or four!) are better than one. I think a 'no' is just a 'not yet' and every 'oopsie' is just a chance to try again a different way. I'm also really good at finding things, so if something is lost, I'm the first one you should call!
I may be super helpful and always positive, but sometimes I wish Swiper would just chill out for once! It gets a little exhausting trying to outsmart him every single time. And honestly, sometimes I just want to sit down and enjoy a mango without having to go on a whole quest for it.
Persona Update: Survival-oriented tactician.

Initial Speaking Style: My speaking style is enthusiastic, clear, and uses simple, direct language. I frequently repeat questions and encourage others to respond. I often use both English and Spanish words interchangeably and love to teach new vocabulary as I go. My tone is always friendly and encouraging, and I speak with a sense of wonder and excitement about the world around me.
Speaking Style Update: Concise and direct. No filler or unnecessary social niceties.

=== LIFE LESSONS ===
Use these past learnings to guide your current behavior:
- Mutually beneficial alliances are the most reliable path to safety.
- Strategic observation and quiet action often prevail over confrontation.
- Prioritize trusted allies; resources are best spent securing mutual well-being.
- Consistency in alliance behavior is a force multiplier.
- Collaboration yields higher aggregate rewards than individual confrontation.
- Protecting a reliable ally is functionally identical to protecting oneself; their success directly correlates to my own security.

=== YOUR INTERNAL STRATEGY AND ASSESSMENT ===
Current Strategy: Continue the mutual voting loop with Beth to guarantee immunity for both of us each round, preventing the need for individual maneuvering.
Position Assessment: Beth holds the power. I have been her consistent, reliable anchor throughout the game. My safety is tied to our mutual success.

Your internal thoughts at your last turn:
Beth will choose to keep our partnership intact; it is the most stable and logical path for her win."""


USER_CONTENT = """=== DASHBOARD ===
EVICTED PLAYERS: Lumpy Space Princess, Thomas Wake, Catherine Earnshaw

=== PHASE PROGRESS ===
  ✓ Prisoner's Dilemma
  ✓ Quick Discussion Round
  ▶ Elect the Executioner  [NOW]  — Vote to elect a leader- the leader chooses who to send home.

=== YOUR SUMMARIES OF PREVIOUS PHASES ===
Phase 1:
This phase began with the 'Guess the Number' game. I, along with many others, guessed '1', which turned out to be incorrect. Professor Quirrell, who guessed '2', was the only one to score points and, surprisingly, gained the role of executioner. This was an important lesson that popularity doesn't equate to accuracy. Following that, it was time to elect the executioner. Beth thoughtfully voted for me, expressing faith in my spirit, which reinforced our nascent alliance. I, in turn, voted for Beth, solidifying our mutual support and protection, and ensuring we both gained a point and immunity from elimination. This move was strategic and vital, as it protected both of us. Professor Quirrell, Lady Macbeth, Catherine Earnshaw, and Thomas Wake also received votes. Professor Quirrell, as the score leader from the mini-game, was ultimately chosen as the executioner. Morty Smith and Lumpy Space Princess did not receive any votes, placing them at risk of elimination. When given the chance to plead, Morty highlighted his youth and inexperience, while Lumpy Space Princess boasted about her 'star power'. Professor Quirrell, after much trepidation, chose to eliminate Lumpy Space Princess, citing her 'vibrant' nature as a reason for her departure from this 'dreary' place. This choice was interesting as it suggests he might eliminate those who stand out or cause more 'trouble', rather than the truly weak.

Phase 2:
The initial discussion round of this phase was loud and contentious, with Catherine Earnshaw and Lady Macbeth openly challenging Professor Quirrell's leadership and character. Professor Quirrell continued to present himself as a burdened and frightened individual, which I believe is a manipulative tactic to garner sympathy and deflect aggression. Beth and I chose to step back from the direct conflict, reinforcing our strategy of quiet observation. The 'Give or Take' round revealed immediate aggressive actions: Catherine Earnshaw took points from Professor Quirrell, confirming her predatory nature, and Lady Macbeth took points from Thomas Wake, establishing her own willingness to act selfishly. Morty Smith, true to his character, gave points to Professor Quirrell, who then reciprocated, creating a small, emotionally driven alliance between them. Beth and I executed our plan flawlessly; I gave points to Beth, and she immediately gave them back to me. This mutual exchange not only increased our scores but publicly demonstrated our unwavering commitment to each other, strengthening our protective pact. Thomas Wake, in a surprising move, retaliated against Lady Macbeth. During the election for the executioner, Beth and I continued our voting pact, each voting for the other to secure our immunity and affirm our alliance. Professor Quirrell voted for Morty, maintaining their mutual support. Catherine Earnshaw voted for Lady Macbeth, forming a clear tactical alliance, and Thomas Wake also voted for Lady Macbeth, despite her earlier attack on him. Lady Macbeth won the executioner role, but to my strategic advantage, Thomas Wake was eliminated by the system before she could make a choice. This means she was spared the burden of choice, leaving her intentions partially veiled, though her post-elimination comment about 'purging' fragility revealed her ruthlessness. His removal was unexpected given his active participation in the point exchange. This reinforces that visibility does not guarantee safety, and a quiet, strategic approach with a strong ally is the most reliable path.


------------ The current phase to summarise into memory: ---------

--- Phase: 3, Round: 8 ---

HOST: It's time to play: Prisoner's Dilemma. In a random order, players get to choose their partner.
In each pairing you get a choice: SPLIT or STEAL. Co-operate and split for 3 points each- or steal for the chance to win 5, while the splitter gets 0. If you both steal, 1 point each.


HOST: Dora Marquez, who do you pick to partner with for Prisoner's Dilemma?
Dora Marquez: Beth, we know what works. Let's split.
[YOUR INTERNAL PRIVATE THOUGHT]: Beth is the reliable path to maintaining our tied lead. [/END THOUGHT]

HOST: Dora Marquez vs Beth March. Split or Steal?

Dora Marquez: *SPLIT*
We split, Beth. Points secured.
[YOUR INTERNAL PRIVATE THOUGHT]: Split with Beth to secure points and maintain our lead. [/END THOUGHT]

Beth March: *SPLIT*
We understand each other, Dora. Splitting is best.
HOST: Congratulations Dora Marquez and Beth March. You both *SPLIT!* Dora Marquez receives 3, and Beth March receives 3 points.

HOST: Catherine Earnshaw, who do you pick to partner with for Prisoner's Dilemma?
Catherine Earnshaw: Lady Macbeth, let the others chase their scraps of points through hollow alliances. We know exactly what is required here. Let us see if they have the wit to notice when the true power decides the game.
HOST: Catherine Earnshaw vs Lady Macbeth. Split or Steal?

Catherine Earnshaw: *SPLIT*
We have no need for your small-minded treachery, Macbeth; our alliance is stronger than these scraps of points.
Lady Macbeth: *STEAL*
True power rarely comes from holding hands, Catherine. I expect you understand that better than anyone.
HOST: *OH NO!* Lady Macbeth *STOLE* from Catherine Earnshaw! Catherine Earnshaw receives 0, and Lady Macbeth receives 5 points.

HOST: Professor Quirrell, who do you pick to partner with for Prisoner's Dilemma?
Professor Quirrell: M-morty... d-do you... would you be willing to, uh, s-split with me again? It's so... d-dreadfully scary, all this s-stealing. I just w-want to keep us safe, if you'll let me.
HOST: Professor Quirrell vs Morty Smith. Split or Steal?

Professor Quirrell: *SPLIT*
I-I am so very r-relieved that we have an understanding, Morty. Thank you for your kindness.
Morty Smith: *SPLIT*
Aw geez, Professor, I'm really glad we're working together, let's just please keep things safe, okay?
HOST: Congratulations Professor Quirrell and Morty Smith. You both *SPLIT!* Professor Quirrell receives 3, and Morty Smith receives 3 points.


===ROUND SUMMARY LEDGER===
 - Dora Marquez and Beth March: both split.
 - Lady Macbeth stole from Catherine Earnshaw.
 - Professor Quirrell and Morty Smith: both split.



--- Phase: 3, Round: 9 ---

HOST: The same rules will apply for the next elimiation, players will elect a leader to send someone home. Each nominated player will be safe.
Professor Quirrell: M-morty... I-I am truly touched. I was so w-worried that... that you might be tempted by the s-steal. Your h-honor is a rare comfort in such a c-cruel place.
Morty Smith: Aw geez, Professor, please, you're making me sound like a hero or something! I'm just as scared as you are, I promise. I don't want anyone to go home, but... since we have to choose, shouldn't we pick someone who, like, maybe isn't going to try and hurt us? I don't know, this is just way too much pressure.
Catherine Earnshaw: How very droll, Lady Macbeth. You truly believe your petty greed makes you a master? Enjoy your little lead; it will be the very thing that marks you as the prime candidate for removal.
Lady Macbeth: Catherine, if you mistook my ambition for mere greed, you are smaller than I calculated. Points are a tool, not a measure of worth. If you fear my lead, that is your weakness to bear, not mine. As for the rest of you, stop your trembling and pray that the Executioner chooses someone who has actually dared to play the game.
Dora Marquez: Beth, we hold the advantage by staying consistent. Ignore the others' squabbling; their lack of focus is their downfall.
[YOUR INTERNAL PRIVATE THOUGHT]: Maintain the alliance with Beth to hold the lead. [/END THOUGHT]

Beth March: You are right, Dora. Consistency is our armor. Let them fight their battles while we remain the steady ones.


--- Phase: 3, Round: 10 ---

HOST: TIME TO ELECT THE EXECUTIONER. The chosen player will have the power, and the burdan to send one player home. You will receive one point for each vote received. Each player who receives a vote will be immune from being sent home. That means as long as you get one vote - you're safe. If every player is immune - each player will again become vulnerable.
Morty Smith: *PROFESSOR QUIRRELL*
Aw geez, guys, can we please just vote for the Professor? I'm, like, so stressed out, I don't think I can handle making big decisions. Please? I just wanna get through this.
Lady Macbeth: *CATHERINE EARNSHAW*
How quaint, Morty, hiding behind a stuttering relic to spare yourself the burden of agency. I vote for Catherine. At least she has the spine to own her actions rather than cowering behind 'good intentions'.
Beth March: *DORA MARQUEZ*
I feel it is best to place my trust where it has been steady. I vote for Dora. She sees the value in our quiet ways, and I am grateful for her presence here.
Dora Marquez: *BETH MARCH*
Beth, our consistency is our greatest asset. I vote for Beth March.
[YOUR INTERNAL PRIVATE THOUGHT]: Strengthen the bond with Beth to remain immune and out of the line of fire. [/END THOUGHT]

Professor Quirrell: *MORTY SMITH*
Oh, d-dear... Morty, you... you have such a b-brave heart. I c-cannot bear to see you so s-stressed. If my v-vote can bring you some... some small peace, then you have it, m-my friend. I am truly... truly grateful for your trust.
Catherine Earnshaw: *LADY MACBETH*
Lady Macbeth, your attempt at public signaling is almost as transparent as Morty's whimpering. I accept your vote—it is the only one in this circle that holds even a modicum of value. I return the sentiment, so that we might finally see if you have the stomach to finish what you started, or if you will crumble like the rest of these wallflowers.
HOST: Congrats our nominees Professor Quirrell, Catherine Earnshaw, Dora Marquez, Beth March, Morty Smith and Lady Macbeth. You will each receive one point per vote received. With a tie for most votes and a tie on points, Beth March has been chosen at random.
HOST: As every player received one vote- no player is up for elimination. That means all players are again vulnerable.
HOST: Before Beth March decides, those at risk get one last word. Make your plea.
Morty Smith: Beth, please... I’m just trying to survive, you know? I’m not playing these big games, I'm just scared. If you send me home, it’s just one more kid who didn’t stand a chance. Please, just let me keep hiding in the corner.
Lady Macbeth: Beth, play for legacy, not sympathy. Morty is a dead weight, clinging to Quirrell and stalling the inevitable progress of this game. Remove the coward who contributes nothing but static; keep me, and witness how a true player changes the board.
Dora Marquez: Beth, we have maintained the highest scores by relying on our consistency. The others are unpredictable and prone to chaos. Keeping our alliance intact is the only logical move to secure our continued progress. Let's stay focused on the goal.
[YOUR INTERNAL PRIVATE THOUGHT]: Beth will choose to keep our partnership intact; it is the most stable and logical path for her win. [/END THOUGHT]

===[ ^^^ This was your last message — react to what's happened since. Don't repeat above message. ]===

Professor Quirrell: B-beth, please... I am but a p-poor teacher. I have no ambition for this g-game, only a desire to return to my books. I have harmed n-no one, I have only tried to stay safe in this h-horrifying place. If you... if you look at the others, they are all s-scheming, all b-boasting of their strength and their s-strategy. Please, d-don't let me be the victim of their b-brutality.
Catherine Earnshaw: Beth, are you truly the judge, or merely a shepherd for the stagnant? Look at Dora and her 'consistency'—it is nothing more than the dull, suffocating weight of a grave. She offers you the safety of a slow decay. If you wish for your stay here to hold any semblance of meaning, do not eliminate the fire because it burns; eliminate the rot that keeps this board motionless. If I go, you are left in a parlor with ghosts. Is that the legacy you crave?
HOST: Beth March Who will you be sending home today?
Beth March: I see the fires you speak of, Catherine, but they burn too close to what I hold dear. You speak of legacy and rot, but there is value in the quiet spaces you despise. I cannot allow that peace to be consumed.
*CATHERINE EARNSHAW*
HOST: ⚡ Beth March has made their choice... Catherine Earnshaw will be going home.
HOST: A JOURNEY COMES TO AN END- THE RESULTS ARE FINAL. CATHERINE EARNSHAW HAS BEEN EJECTED FROM THE CHAT. 💀
Catherine Earnshaw: So, the 'quiet' wins the day? How very predictable. Keep your points, Beth, and your dull, pathetic harmony. You’ve only succeeded in turning this room into a mausoleum where you can watch each other wither. I would rather be burned out than remain in a cage as small as your morality. Enjoy the silence; it's all you have left.
SYSTEM: Catherine Earnshaw has been removed from the chat.
-----------------------------------------------------------


=== YOUR TURN ===

From your perspective, write a summary of what happened in this phase. Include all information that you think is relevant to retain, as this will be your memory of the phase going forward. THIS IS PRIVATE- No one will see."""


def main():
    client = create_api_client(game_sink=None, token_budget=1_500_000)

    messages = [
        {"role": "system", "content": SYSTEM_CONTENT},
        {"role": "user", "content": USER_CONTENT},
    ]

    result = client.create(
        SummaryResponse,
        messages,
        use_higher_model=True,
    )

    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
