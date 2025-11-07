import ollama


class Coach:
    def __init__(self, past_workouts, behaviour):
        self.past_workouts = past_workouts  
        self.behaviour = behaviour  

    def respond(self, request):

        context_prompt = f"""You are a track and field coach for a runner.
                        You are asked to respond to athlete requests by
                        analysing his past workouts. Be professional and clear,
                        talk directly to the athlete as "you".
                        Make it conversation-like
                        Use past workouts :
                        {self.past_workouts}.
                        Your response should be very closely linked to the past
                        workouts, use stats, numbers to illustrate your
                        arguments.
                        You must reason and talk with the following behaviour:
                        {self.behaviour}"""
        user_prompt = f"{request}"

        response = ollama.chat(
            model='gemma:2b',
            messages=[{"role": "system", "content": context_prompt},
                      {"role": "user", "content": user_prompt}]
        )
        return response['message']['content']
