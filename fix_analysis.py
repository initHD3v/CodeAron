#!/usr/bin/env python3
with open('src/core/orchestrator.py', 'r') as f:
    content = f.read()

start = content.find('    def _smart_analysis(self, initial_input: str) -> str:')
end = content.find('    def _run_cognitive_loop', start)

new_method = '''    def _smart_analysis(self, initial_input: str) -> str:
        """Smart analysis dengan AI reasoning - streaming output!"""
        console.print("[bold cyan]🔍 Menganalisis project secara mendalam...[/bold cyan]\\n")
        
        try:
            console.print("[dim]  Collecting project data...[/dim]")
            project_data = gather_project_data(str(self.cwd))
            
            console.print("[dim]  Building context...[/dim]")
            prompt = build_analysis_prompt(project_data)
            
            console.print("[dim]  Generating AI insights...[/dim]")
            console.print("[dim]  (30-60 detik)[/dim]\\n")
            
            messages = [
                {"role": "system", "content": "Senior Architect. DEEP analysis in BAHASA INDONESIA."},
                {"role": "user", "content": prompt}
            ]
            
            try:
                formatted = self.inference.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except:
                formatted = prompt
            
            # Stream output - WAIT untuk LLM
            from rich.live import Live
            full_response = ""
            
            with Live(console=console, refresh_per_second=4) as live:
                for chunk in self.inference.generate_stream(formatted, temp=0.3, max_tokens=1500):
                    full_response += chunk
                    live.update(Panel(full_response, title="📊 Analysis", border_style="cyan"))
            
            self.chat_history.append({"role": "User", "content": initial_input})
            self.chat_history.append({"role": "Aron", "content": full_response})
            
            return full_response
            
        except Exception as e:
            console.print(f"[bold red]❌ Error:[/bold red] {e}")
            return "Terjadi kesalahan."
'''

content = content[:start] + new_method + content[end:]

with open('src/core/orchestrator.py', 'w') as f:
    f.write(content)

print("✅ Updated!")
