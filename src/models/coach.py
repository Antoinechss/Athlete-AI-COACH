import ollama
from config.personas import COACH_PERSONALITIES

class Coach:
    def __init__(self, past_workouts, persona):
        self.past_workouts = past_workouts
        self.persona = persona
        self.behaviour = COACH_PERSONALITIES[persona]["behaviour"]

    def respond(self, request):
        # Check if we have actual workout data
        workout_analysis = ""
        if self.past_workouts and len(self.past_workouts) > 0:
            workout_analysis = f"""
            Here are the athlete's recent workouts to analyze:
            {self.past_workouts}
            
            IMPORTANT: 
            - Reference specific workout dates, distances, times, and heart rates
            - Compare recent performances to identify trends
            - Give concrete advice based on the actual data
            - Mention specific numbers from the workouts
            """
        else:
            workout_analysis = "No recent workout data available. Ask the athlete to sync their Strava data first."

        context_prompt = f"""
                        You are {self.persona} as a track and field coach. 
                        
                        {workout_analysis}
                        
                        Rules for your response:
                        - ALWAYS reference specific workout data if available (dates, distances, paces, heart rates)
                        - Be direct and analytical like {self.persona}
                        - Maximum 4 sentences
                        - If no workout data, ask them to sync their workouts first
                        - Don't hallucinate or make up workout details
                        
                        Coach personality context: {self.behaviour}
                        """

        user_prompt = f"Athlete question: {request}"

        response = ollama.chat(
            model='gemma:2b',
            messages=[{"role": "system", "content": context_prompt},
                    {"role": "user", "content": user_prompt}]
        )
        return response['message']['content']