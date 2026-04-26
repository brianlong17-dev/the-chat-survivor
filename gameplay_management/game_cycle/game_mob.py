import random
import time 
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from gameplay_management.base_manager import BaseRound
from models.player_models import DynamicModelFactory
from prompts.gamePrompts import GamePromptLibrary

if TYPE_CHECKING:
    from agents.player import Debater

@dataclass
class Mob:
    leader: "Debater"
    target: str  # target's name
    followers: list["Debater"]

class GameMob(BaseRound):

    @classmethod
    def display_name(cls, cfg):
        return "Mob Mentality"

    @classmethod
    def rules_description(cls, cfg):
        return (
            "Players can nominate themselves as mob leaders and announce a target. "
            "All other players secretly pledge to a mob. Smaller mobs are disbanded and members choose again. "
            "This repeats until two mobs remain. The larger mob wins — the target loses ALL their points, "
            "split among the winning mob members. In a tie, each target loses half."
        )
        
    ####################
    #
    # --- Narration ---#
    #
    ####################

    def _consolodating_string(self, group):
        return self.format_list([self._mob_label(mob, True) for mob in group])

    def _react_to_mob_initiation(self, agent, mob):
        target_name = ': Pass' if not mob else f" targets {mob.target}"
        self._host_broadcast(f"{agent.name}{target_name}")
        return
            
        if mob is None:
            self._host_broadcast_multiple_choice([
                f"{agent.name} plays it safe... they will not be a mob leader.",
                f"{agent.name}, always the diplomat — they pass.",
                f"{agent.name} chooses no one. They will remain a follower.",
            ])
        else:
            self._host_broadcast_multiple_choice([
                f"{agent.name} has chosen {mob.target}. A cold choice.",
                f"{agent.name} marks their target: {mob.target} has been chosen.",
                f"{agent.name} picks {mob.target} as their target. Will others join them?",
            ])
      
      
    def _mob_label(self, mob, incl_followers = False):
        size = len(mob.followers)
        follower_str = ""
        if incl_followers:
            follower_str = f", {size} follower" if size == 1 else f", {size} followers"
        return f"{mob.leader.name}'s mob ({mob.target}{follower_str})"

    def _mobs_string(self, mobs):
        return "\n".join(f"- {self._mob_label(mob, True)}" for mob in mobs)

            
    def _annouce_mobs(self, mobs, is_intro=False):
        if is_intro:
            leader_names = self.format_list([mob.leader.name for mob in mobs])
            output_string = f"After the nomination round, {len(mobs)} mobs have been formed: \n"
            for mob in mobs:
                output_string += f"{(self._mob_label(mob, False))}\n"
            output_string += "\n"
            self._host_broadcast(output_string)
        else:
            self._host_broadcast("Our mobs as they now stand:")
            for mob in mobs:
                follower_names = self.format_list([f.name for f in mob.followers]) if mob.followers else "no followers yet"
                self.gameBoard.host_broadcast(
                    f"{self._mob_label(mob, True)} — members: {follower_names}"
                )
    
    def _host_rephrase(self, message):
        #give this to a method on gamemaster
        #it should translate it into a new turn of phrase
        #smallest possible model
        #also stream the response.
        pass
    
    
    @classmethod
    def is_game(cls):
        return True

    def _force_choice(self, agent):
        
        questions = [f"{agent.name}, as an unwilling leader, who do you choose to target? ",
                     f"Unfortunately {agent.name}, the time to follow is over- now it's time to lead. Who will you target? ",
                     f"Some are born to lead, others... have leadership thrust upon them. {agent.name}, you time has come. Who will you target? "]
        self._host_broadcast_multiple_choice(questions)
        
        valid_targets = [a.name for a in self.agents if a.name != agent.name]
        action_fields = self.create_choice_field(
            "mob_choice",
            valid_targets,
            "You have been chosen as a mob leader. You must pick a target — no passing."
        )
        model = DynamicModelFactory.create_model_(
            agent,
            action_fields=action_fields,
            public_response_prompt="Announce your target to the group.",
            additional_thought_nudge="You have no choice but to lead. Who do you go after?"
        )
        self.gameBoard.host_broadcast(f"No one stepped up — {agent.name}, you've been drafted as a mob leader!")
        result = agent.take_turn_standard(
            f"You've been forced into leadership. You must choose a target: {self.format_list(valid_targets)}",
            self.gameBoard, model
        )
        self.gameBoard.handle_public_private_output(agent, result)
        choice = result.mob_choice.strip()
        if choice in valid_targets:
            return Mob(agent, choice, [])
        
        else:
            fallback = random.choice(valid_targets)
            self.private_system_message(agent, f"Invalid choice '{choice}' — {fallback} was assigned as your target.")
            return Mob(agent, fallback, [])

    def _other_agents(self, agent, agents):
        return [a for a in agents if a != agent]

    def _force_mob_leaders(self):
        agents_to_choose = random.sample(self.agents(), 2)
        mobs = []
        self.gameBoard.host_broadcast(f"Since no one stepped up, {agents_to_choose[0].name} and {agents_to_choose[1].name} have been selected to be mob leaders.")
        for agent in agents_to_choose:
            mob = self._force_choice(agent)
            self._react_to_mob_initiation(agent, mob)
            mobs.append(mob)
        return mobs
        
    def _decide_to_be_leader(self, agent, other_agents):
        lines = [
            f"{agent.name} — will you lead, or follow?",
            f"{agent.name}, the time has come. Will you step up, or sit back?",
            f"A mob needs a leader. {agent.name} — do you have what it takes?",
        ]
        #self._host_broadcast_multiple_choice(lines)
        valid_targets = [a.name for a in other_agents if a.name != agent.name]
        choices = ["pass"] + valid_targets

        action_fields = self.create_choice_field(
            "mob_choice",
            choices,
            "Choose a player to target as mob leader, or 'pass' to remain a follower. Leaders earn double points if their mob wins."
        )
        model = DynamicModelFactory.create_model_(
            agent,
            action_fields=action_fields,
            public_response_prompt=(f"If you chose to lead a mob, declare yourself and your target. If you pass, leave this blank. "
                                    "Give your initial pitch as to why others should join your mob. "),
            additional_thought_nudge=(
                "Should you step up as leader? Who is your biggest threat? "
                "Could you rally others against them? Remember — leaders earn double points if their mob wins, "
                "but you also paint a target on yourself."
            )
        )
        user_content = (
            f"You can nominate yourself as a mob leader now. "
            f"Choose a target to mob, or pass to wait and join someone else's mob. "
            f"Valid targets: {self.format_list(valid_targets)}"
        )
        result = agent.take_turn_standard(user_content, self.gameBoard, model)
        self.gameBoard.handle_public_private_output(agent, result)
        
        choice = result.mob_choice.strip()
        if choice == "pass":
            return None
        elif choice in valid_targets:
            return Mob(agent, choice, [])
        else:
            self.private_system_message(agent, f"Invalid target choice '{choice}' — your nomination has been ignored.")
            return None
    
    def _choose_to_join_mobs(self, mobs, followers):
        tasks = [(mobs, follower) for follower in followers]
        results = self._run_tasks(tasks, self._make_mob_choice)
        for follower, result in results:
            time.sleep(1)
            self._handle_mob_choice_response(mobs, follower, result)

    def _handle_mob_choice_response(self, mobs, follower, result):
        self.gameBoard.handle_public_private_output(follower, result)
        choice = result.mob_choice.strip()
        chosen_mob = next((m for m in mobs if self._mob_label(m, False) == choice), None)
        if not chosen_mob:
            chosen_mob = random.choice(mobs)
            self.private_system_message(follower, f"{follower.name} made an invalid choice '{choice}' — they have been randomly assigned to {self._mob_label(chosen_mob, False)}.")
        else:
            self._host_broadcast(f"{follower.name} has chosen to join {self._mob_label(chosen_mob)}")
        chosen_mob.followers.append(follower)
    
             
    def _make_mob_choice(self, mobs, follower, rejoining = False):
        lines = [
            f"{follower.name} — which mob will you join?",
            f"The mobs await. {follower.name}, where do you pledge your loyalty?",
            f"{follower.name}, choose your side.",
        ]
        #self._host_broadcast_multiple_choice(lines)
        choices = [self._mob_label(mob, False) for mob in mobs]
        action_fields = self.create_choice_field(
            "mob_choice",
            choices,
            "Choose which mob to join."
        )
        model = DynamicModelFactory.create_model_(
            follower,
            action_fields=action_fields,
            public_response_prompt="What do you say as you pledge to your chosen mob?",
            additional_thought_nudge="Who do you trust? Who do you think will win? Who is targeting your enemies?"
        )
        prompt = f"The following mobs have been formed:\n{self._mobs_string(mobs)}\nChoose one to join."
        if rejoining:
            rejoining_prompt = f"Your mob was the smallest and has been disbanded. Time to choose a new tribe. \n"
            prompt = prompt + rejoining_prompt
        result = follower.take_turn_standard(
            prompt,
            self.gameBoard, model
        )
        return follower, result

   
    def _consolodate_mobs(self, mobs):
        grouped = defaultdict(list)
        for mob in mobs:
            grouped[mob.target].append(mob)

        needs_consolidation = any(len(group) > 1 for group in grouped.values())
        if needs_consolidation:
            self.gameBoard.host_broadcast(
                "We will now consolidate mobs targetting the same person. "
            )

        new_mobs = []
        for target, group in grouped.items():
            if len(group) == 1:
                new_mobs.append(group[0])
                continue
            output_string = f"We have {len(group)} mobs targeting {target}. "

            group.sort(key=lambda m: len(m.followers), reverse=True)
            top_count = len(group[0].followers)
            tied = [m for m in group if len(m.followers) == top_count]

            if len(tied) == 1:
                winner = tied[0]
                output_string += f"{winner.leader.name} had the most followers — they take control of the mob. "
            else:
                # Tiebreak by points
                tied.sort(key=lambda m: self.gameBoard.agent_scores[m.leader.name], reverse=True)
                top_points = self.gameBoard.agent_scores[tied[0].leader.name]
                points_tied = [m for m in tied if self.gameBoard.agent_scores[m.leader.name] == top_points]

                if len(points_tied) == 1:
                    winner = points_tied[0]
                    output_string = f"Two mobs were equal in size — but {winner.leader.name} has more points, so they take the lead. "
                    
                else:
                    winner = random.choice(points_tied)
                    self.gameBoard.host_broadcast(
                        f"As the top leaders had equal points, {winner.leader.name} was chosen at random to take command. "
                    )

            # Losing leaders become followers of the winner
            for mob in group:
                if mob is winner:
                    continue
                winner.followers.append(mob.leader)
                winner.followers.extend(mob.followers)
            output_string += f"The mob now has {len(winner.followers)} followers. \n\n"

            self.gameBoard.host_broadcast(output_string)
            new_mobs.append(winner)

        return new_mobs

    def _split_points(self, mob):
        points_to_take = self.gameBoard.agent_scores[mob.target]
        self.gameBoard.append_agent_points(mob.target, -points_to_take)
        total_shares = len(mob.followers) + 2
        share = points_to_take // total_shares
        if share < 1:
            share = 1
            self.gameBoard.host_broadcast(
                f"{mob.target} didn't have enough points to go around — "
                f"each mob member earns 1 point, and {mob.leader.name} earns 2 as leader."
            )
        self.gameBoard.append_agent_points(mob.leader.name, share * 2)
        for follower in mob.followers:
            self.gameBoard.append_agent_points(follower.name, share)   
        return points_to_take
    
    def _disband_mob(self, mobs, mob):
        self.gameBoard.host_broadcast(f"{self._mob_label(mob)} is the smallest — they are disbanded.")
        free_agents = [mob.leader] + mob.followers
        mobs.remove(mob)
        self.gameBoard.host_broadcast(
            f"{self.format_list([a.name for a in free_agents])}, you are now free — choose a new mob."
        ) #ok this needs an if - is there always free agents?
        #self._make_pitch(mobs, free_agents) 
        for agent in free_agents:
            follower, result = self._make_mob_choice(mobs, agent, rejoining=True)
            self._handle_mob_choice_response(mobs, follower, result)
            
        # self._run_tasks(
        #     [(mobs, agent) for agent in free_agents],
        #     lambda mobs, agent: self._choose_to_join_mobs(mobs, agent, rejoining=True)
        # )
        
    def _make_pitch(self, mobs, free_agents):
        free_names = self.format_list([a.name for a in free_agents])
        self.gameBoard.host_broadcast(
            f"{free_names} — it's time to choose your side. But first, let's hear from the leaders."
        )
        for mob in mobs:
            self._host_broadcast_multiple_choice([
                f"{mob.leader.name}, as a mob leader, why should they join your mob targeting {mob.target}? Should they be afraid not to? ",
                f"{mob.leader.name} — all of a sudden you're in position of power- time to make your case. Why should the free agents join you?",
                f"The floor is yours, {mob.leader.name}. Should they join you?",
            ])
            self._basic_turn(
                mob.leader,
                f"{free_names} must now choose which mob to join.  Why should they join your mob targeting {mob.target}?",
                "Your pitch to the free agents.",
                optional=False
            )

        self.gameBoard.host_broadcast("And now — a word from the targets.")
        for mob in mobs:
            target = self._agent_by_name(mob.target)
            if target:
                self._host_broadcast_multiple_choice([
                    f"{target.name}, you're in a rough spot. What do you say to someone considering joining the mob against you?",
                    f"How does it feel, {target.name}? The mob is growing — do you have anything to say?",
                    f"{target.name} — now's your chance. Can you turn the tide?",
                ])
                self._basic_turn(
                    target,
                    f"{free_names} are considering joining the mob targeting you. This is your opportunity to plead your case. ",
                    "Your public words. ", 
                    optional=False
                )
        
    def _finale(self, mobs):
        mob_a, mob_b = mobs[0], mobs[1]
        size_a = len(mob_a.followers) + 1
        size_b = len(mob_b.followers) + 1

        self.gameBoard.host_broadcast(
            f"Two mobs remain: \n"
            f"- {self._mob_label(mob_a, True)}\n"
            f"- {self._mob_label(mob_b, True)}"
        )

        if size_a != size_b:
            winner, loser = (mob_a, mob_b) if size_a > size_b else (mob_b, mob_a)
            self.gameBoard.host_broadcast(
                f"{self._mob_label(winner)} is the larger mob — they win!"
            )
        else:
            # tiebreak by leader points
            score_a = self.gameBoard.agent_scores[mob_a.leader.name]
            score_b = self.gameBoard.agent_scores[mob_b.leader.name]
            if score_a != score_b:
                winner, loser = (mob_a, mob_b) if score_a > score_b else (mob_b, mob_a)
                self.gameBoard.host_broadcast(
                    f"It's a tie on size — but {winner.leader.name} has more points and takes command of the win!"
                )
            else:
                winner, loser = random.choice([(mob_a, mob_b), (mob_b, mob_a)])
                self.gameBoard.host_broadcast(
                    f"Too close to call — it came down to luck. {winner.leader.name}'s mob wins!"
                )

        self.gameBoard.host_broadcast(f"{winner.target} loses everything.")
        points_value = self._split_points(winner)

        # Reactions — target responds, then winning mob members
        target = self._agent_by_name(winner.target)
        if target:
            self._basic_turn(target, "You've been mobbed. React.", "Your reaction.", optional=False)
        self._basic_turn(winner.leader, "Your mob won. React.", "Your reaction.", optional=False)
        mobs.remove(loser)
        return points_value

    def _redemption(self, mob, points):
        host_string = (f"Well you've all left {mob.target} penniless. You have one last chance for peace: "
        "You have the opportunity to return the points gained.")
        self._host_broadcast(host_string)
        self._choose_redemption(mob.leader, mob.target, points * 2)
        for follower in mob.followers:
            self._choose_redemption(follower, mob.target, points)

    def _choose_redemption(self, mobster, target, points):
        action_fields = self.create_choice_field(
            "redemption_choice", ["Yes", "No"], "Do you choose to give back the points or keep them? "
        )
        model = DynamicModelFactory.create_model_(
            mobster,
            action_fields=action_fields,
            public_response_prompt="What do you say to the target, and the group?",
            additional_thought_nudge="Are they a threat? Is it worth it? "
        )
        result = mobster.take_turn_standard(
            f"Make your choice, give back the points or keep 'em.",
            self.gameBoard, model
        )
        self.gameBoard.handle_public_private_output(mobster, result)
        choice = result.redemption_choice.strip()
        if choice == "Yes":
            self.gameBoard.host_broadcast(f"{mobster.name} gives back the points!")
            self.gameBoard.append_agent_points(mobster.name, -points)
            self.gameBoard.append_agent_points(target, points)

            
        
        
    def _reconsider(self, mobs, get_a_point=False):
        announcement = f"Followers - you now have a chance to reconsider. You may switch mobs, or remain where you are."
        if get_a_point:
            announcement += " If you choose to switch, you will earn 1 point."
        self.gameBoard.host_broadcast(announcement)

        followers = [f for mob in mobs for f in mob.followers]
        if get_a_point:
            for follower in followers:
                self._change_sides(mobs, follower, get_a_point=True)
        else:
            self._run_tasks(
                [(mobs, follower) for follower in followers],
                lambda mobs, follower: self._change_sides(mobs, follower, get_a_point=False)
            )

    def _change_sides(self, mobs, player, get_a_point=False):
        current_mob = next((m for m in mobs if player in m.followers), None)
        other_mobs = [m for m in mobs if m is not current_mob]
        choices = [self._mob_label(m, False) for m in other_mobs] + ["stay"]
        action_fields = self.create_choice_field(
            "mob_choice", choices, "Choose a mob to switch to, or 'stay' to remain where you are."
        )
        nudge = (
            "You will earn 1 point if you switch — but consider whether the loyalty cost is worth it."
            if get_a_point else
            "Stay silent and leave this blank unless you are switching. Silence means you stay."
        )
        model = DynamicModelFactory.create_model_(
            player,
            action_fields=action_fields, #maybe we do need to add optional here
            public_response_prompt="If you are switching, say something as you cross the floor. Otherwise leave this blank.",
            additional_thought_nudge=nudge
        )
        result = player.take_turn_standard(
            f"The mobs as they stand:\n{self._mobs_string(mobs)}\nYou are currently in {self._mob_label(current_mob, False)}. Will you stay or switch?",
            self.gameBoard, model
        )
        choice = result.mob_choice.strip() if result.mob_choice else "stay"
        chosen_mob = next((m for m in other_mobs if self._mob_label(m, False) == choice), None)
        if choice == "stay" or not chosen_mob:
            if choice not in ("stay", "") and not chosen_mob:
                self.private_system_message(player, f"Invalid choice '{choice}' — you remain in {self._mob_label(current_mob, False)}.")
            return self.gameBoard.handle_public_private_output(player, result)
        current_mob.followers.remove(player)
        chosen_mob.followers.append(player)
        if get_a_point:
            self.gameBoard.append_agent_points(player.name, 1)
        self.gameBoard.handle_public_private_output(player, result)
        self.gameBoard.host_broadcast(f"{player.name} switches to {self._mob_label(chosen_mob, False)}!")
        
        
    def run_game(self):
        mobs: list[Mob] = []
        agents = self._shuffled_agents()
        host_intro = ("Welcome to Mob Mentality- the game where you will be a Mob Boss- or a Henchmen. "
        "Mob rules- only the biggest mob will get their target...and share their points. "
        "We will start with a choice: will you pick a target and lead the mob? "
        "Or wait to see where the wind is blowing, and join the mob? ")
        self._host_broadcast(host_intro)
        
        for agent in agents: 
            mob = self._decide_to_be_leader(agent, agents)
            self._react_to_mob_initiation(agent, mob)
            if mob:
                mobs.append(mob)

        if not mobs:
            mobs = self._force_mob_leaders()

        if len(mobs) == 1:
            self.gameBoard.host_broadcast(f"Only one person was brave enough to step forward — {mobs[0].leader.name} will reap the rewards.")
            self._split_points(mobs[0])
            return
        
        self._annouce_mobs(mobs, True)
        leaders = [mob.leader for mob in mobs]
        followers = [agent for agent in agents if agent not in leaders]
        if followers:
            self._host_broadcast(f"Now our undeclared players must make a decision. {self.format_list([a.name for a in followers])}.")
       
        
        self._choose_to_join_mobs(mobs, followers)

        mobs = self._consolodate_mobs(mobs)

        while len(mobs) > 2:
            self._annouce_mobs(mobs)
            smallest = min(mobs, key=lambda m: len(m.followers) + 1)
            self._disband_mob(mobs, smallest)
            self._reconsider(mobs, True)

        points = self._finale(mobs)
        self._redemption(mobs[0], points)

      