import sys
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.status import Status
import llm_client
import safety
import executor
import logging

console = Console()

def display_plan(response: llm_client.AgentResponse):
    """
    Display the proposed plan in a nice table.
    """
    console.print(Panel(Markdown(f"**Thought Process:** {response.thought_process}"), title="Agent Reasoning", border_style="blue"))
    
    table = Table(title="Proposed Actions")
    table.add_column("Risk", justify="center")
    table.add_column("Command", style="cyan")
    table.add_column("Description")

    for action in response.proposed_actions:
        risk_style = "green"
        if action.risk_level.upper() == "MEDIUM":
            risk_style = "yellow"
        elif action.risk_level.upper() == "HIGH":
            risk_style = "red bold"
            
        table.add_row(
            f"[{risk_style}]{action.risk_level}[/{risk_style}]",
            action.command,
            action.description
        )
    
    console.print(table)
    console.print(f"[bold green]Agent says:[/bold green] {response.user_response}\n")

def main():
    console.print(Panel.fit("[bold blue]DietPi SysAdmin Agent[/bold blue]\nType 'exit' or 'quit' to stop.", border_style="blue"))
    
    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")
        
        if user_input.lower() in ['exit', 'quit']:
            console.print("[yellow]Goodbye![/yellow]")
            break
            
        if not user_input.strip():
            continue

        try:
            with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
                response = llm_client.get_agent_response(user_input)
            
            display_plan(response)
            
            # Execution Phase
            all_executed = True
            execution_results = []

            for action in response.proposed_actions:
                # Safety Check
                is_safe, reason = safety.check_safety(action.command, action.risk_level)
                
                proceed = True
                if not is_safe:
                    console.print(f"[bold red]SAFETY WARNING:[/bold red] {reason}")
                    proceed = Confirm.ask("Do you want to execute this command?")
                
                if proceed:
                    with console.status(f"[bold yellow]Executing:[/bold yellow] {action.command}", spinner="simpleDots"):
                        result = executor.execute_command(action.command)
                        execution_results.append(result)
                        
                    if result['success']:
                        console.print(f"[green]✔ Success[/green]: {action.command}")
                        if result['stdout']:
                            console.print(Panel(result['stdout'], title="Output", border_style="dim white"))
                    else:
                        console.print(f"[red]✘ Failed[/red]: {action.command}")
                        console.print(f"[red]Error:[/red] {result['stderr']}")
                        all_executed = False
                        # Stop chain on failure? Usually safer to stop.
                        if Confirm.ask("Command failed. Stop remaining actions?", default=True):
                            break
                else:
                    console.print("[yellow]Action skipped by user.[/yellow]")
                    all_executed = False
                    break # Stop chain if user declines one
            
            # Log the interaction
            safety.log_action(user_input, response.model_dump(), all_executed)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            logging.error(f"Main loop error: {str(e)}")

if __name__ == "__main__":
    main()

