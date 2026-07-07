import time
from typing import Iterable

import questionary

from core.sinks.console_renderer import ConsoleRenderer
from core.game_context.models import MessageBlock
from core.sinks.game_sink import GameEventSink, Speaker


class ConsoleGameEventSink(GameEventSink):
    """
    Routes all game events to the terminal via ConsoleRenderer.
    Default sink for live runs.
    """
    line_break = (f"\n{"="*50}")
    
    def get_user_input_simple(self, field_name, description):
        print(f"\n▶ {field_name.upper()}")
        print(f"  Goal: {description}")
        return input("  >> ")

    def get_user_input_multiple_choice(self, field_name, description, choices):
        print(f"\n▶ {field_name.upper()}")
        choice = questionary.select(description, choices=choices).ask()
        return choice
    
    def wait_for_continue_next_round(self):
        pass
        #input("continue next round?")  

    def _request_continue_next_round(self):
        pass  # no-op
    
    def on_game_intro(self, message: str) -> None:
        ConsoleRenderer.print_public_action("HOST", message)

    def on_linebreak(self) -> None:
        ConsoleRenderer.print_system_private(self.line_break)

    def on_game_over(self, winner_names: list[str]) -> None:
        if not winner_names:
            result = "No one wins :("
        elif len(winner_names) == 1:
            result = f"🏆 FINAL SURVIVOR: {winner_names[0]}"
        else:
            names = ' & '.join(winner_names)
            result = f"{'🏆' * len(winner_names)} FINAL SURVIVORS: {names}"
        ConsoleRenderer.print_system_private(result)

    def on_phase_header(self, phase_number: int) -> None:
        ConsoleRenderer.print_system_private(self.line_break)
        ConsoleRenderer.print_system_private(f"\nPHASE: {phase_number}")
        ConsoleRenderer.print_system_private(self.line_break)

    def on_phase_intro(self, host_text: str, summary_text: str) -> None:
        ConsoleRenderer.print_public_action("HOST", host_text)
        ConsoleRenderer.print_private("", summary_text, "SYS")

    def on_phase_rounds(self, rounds: list[str]) -> None:
        pass

    def on_phase_round_index(self, index: int) -> None:
        pass

    def on_round_start(self, round_number: int, score_string: str) -> None:
        ConsoleRenderer.print_public_action("SYSTEM", score_string)
        ConsoleRenderer.print_public_action("SYSTEM", f"BEGIN ROUND {round_number}")

    def on_round_summary(self, summary: str) -> None:
        ConsoleRenderer.print_private("SUMMARY", f"{summary}\n", color_name="YELLOW")

    def on_public_action(self, speaker: Speaker, message: str, color: str = "",
                         animate_as_player = False, should_hold: bool = True, directed_to_name = None, 
                         is_reply: bool = False, is_human: bool = False) -> None:
        if directed_to_name:
            message = f"@{directed_to_name} - {message}"
        ConsoleRenderer.print_public_action(speaker, message, color)

    def on_private_thought(self, speaker: Speaker, message: str) -> None:
        ConsoleRenderer.print_private(speaker, message, print_name=False)

    def on_private_conversation(self, message_block: MessageBlock):
        names = ' & '.join(message_block.visibility_restriction) if message_block.visibility_restriction else 'Unknown'
        ConsoleRenderer.print_system_private(f"[Private: {names}]")
        for message_entry in message_block.message_entries:
            speaker = message_entry.speaker
            color = "SYS" if speaker.lower() == 'system' else "RED"
            ConsoleRenderer.print_public_action(speaker, message_entry.public_output, color)
        ConsoleRenderer.print_system_private(f"[End Private]")
       

    def system_private(self, message: str, border_bottom: bool = False) -> None:
        ConsoleRenderer.print_system_private(message)
        if border_bottom:
            ConsoleRenderer.print_system_private('----')

    def system_public(self, message: str, border_bottom: bool = False) -> None:
        self.system_private(message, border_bottom=border_bottom)
        
    def on_inner_workings(
        self,
        speaker: Speaker,
        inner_workings: Iterable[tuple[str, object]],
        override: bool = False,
    ) -> None:
        if override: #or setting
            for key, value in inner_workings:
                formatted_key = key.replace('_', ' ').title() 
                message = f"{formatted_key} : {value}"
                self.on_private_thought(speaker, message)
        

    def on_warning(self, message: str) -> None:
        ConsoleRenderer.print_system_private(f"⚠ {message}")

    def delay(self, delay: float = 0.0) -> None:
        time.sleep(delay)
        
    def on_points_update(self, points: dict[str, int]) -> None:
        pass

    def on_evictions_update(self, evicted_names: list[str]) -> None:
        pass
    
    def _on_user_private_conversation(self, restricted_users, player_name, message):
        pass
