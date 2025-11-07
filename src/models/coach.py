import ollama


class Coach:
    def __init__(self, past_workouts, persona):
        self.past_workouts = past_workouts
        self.persona = persona

    def respond(self, request):

        context_prompt = f"""
                        You are playing the role of {self.persona} as a track and
                        field coach for a runner. You are asked to respond to athlete 
                        requests by analysing his past workouts. Be professional and clear,
                        talk directly to the athlete as "you". You must reason and 
                        talk {self.persona}, add expressions, mimics and think like him/her.
                        Make it conversation-like with the athlete. 
                        Use past workouts for records :
                        {self.past_workouts}.
                        Your response should be very closely linked to the past
                        workouts, use stats, numbers to illustrate your
                        arguments."""

        user_prompt = f"{request}"

        response = ollama.chat(
            model='gemma:2b',
            messages=[{"role": "system", "content": context_prompt},
                      {"role": "user", "content": user_prompt}]
        )
        return response['message']['content']
