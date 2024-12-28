import os
from dotenv import load_dotenv
import google.generativeai as genai

class MeetingMinutesGenerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found in .env file.")
    
        genai.configure(api_key=self.api_key)

        # Set up generation configuration for chunks
        self.chunk_generation_config = {
            "temperature": 0.7,  # Moderate temperature for detailed but focused responses
            "top_p": 0.9,        # Top-p setting for diversity
            "top_k": 50,         # Tokens to sample from
            "max_output_tokens": 2000  # Allowing larger chunks for detailed output
        }

        # Set up generation configuration for final meeting minutes
        self.final_generation_config = {
            "temperature": 0.8,  # A slightly higher temperature for more creativity and elaboration
            "top_p": 0.95,       # Slightly higher top_p for more diversity in responses
            "top_k": 100,        # Allowing more tokens to be considered for a richer output
            "max_output_tokens": 5000  # Allowing a larger output to accommodate detailed paragraphs
        }

        self.model_name = "gemini-pro"

    def _split_transcript(self, transcript, max_length=4000):
        words = transcript.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _generate_chunk_minutes(self, chunk, index):
        prompt = (
            f"You are an assistant tasked with summarizing meeting transcripts into structured meeting minutes. "
            f"Extract key points and organize them under the following sections: "
            f"1. Meeting Title, 2. Date and Time, 3. Attendees, 4. Agenda, 5. Discussion Points, "
            f"6. Decisions Made, 7. Action Items, and 8. Next Meeting Details. "
            f"Ensure that each section is detailed and includes explanations, examples, or relevant information. "
            f"Provide full paragraphs under each section, with enough detail to capture the essence of the meeting. "
            f"Here's part {index + 1} of the transcript:\n\n{chunk}"
        )
        try:
            # Generate detailed minutes for the chunk
            model = genai.GenerativeModel(self.model_name, generation_config=self.chunk_generation_config)
            response = model.generate_content(prompt)
            return response.result
        except Exception as e:
            return f"Error processing chunk {index + 1}: {str(e)}"

    def generate(self, transcript):
        # Split the transcript into manageable chunks
        chunks = self._split_transcript(transcript)
        chunk_minutes = []

        # Process each chunk and collect meeting minutes
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}...")
            minutes = self._generate_chunk_minutes(chunk, i)
            chunk_minutes.append(minutes)

        # Combine all chunk minutes into a single cohesive document
        combined_minutes = "\n\n".join(chunk_minutes)
        
        # Final prompt with expanded details
        final_prompt = (
            "You are an assistant tasked with creating a detailed, comprehensive meeting minutes document. "
            "For each section below, provide full, elaborated paragraphs with detailed explanations, examples, "
            "and sufficient context. Avoid being overly concise. Focus on providing detailed descriptions of the key points, "
            "decisions made, and action items discussed. Make sure each section is clear, with examples and enough information "
            "to understand the discussions and decisions fully. The sections you should cover are:\n\n"
            f"{combined_minutes}\n\n"
            "Please ensure the following sections are fully explained: Meeting Title, Date and Time, Attendees, Agenda, "
            "Discussion Points, Decisions Made, Action Items, and Next Meeting Details."
        )

        try:
            # Generate final detailed meeting minutes using the final generation configuration
            model = genai.GenerativeModel(self.model_name, generation_config=self.final_generation_config)
            final_response = model.generate_content(final_prompt)
            return final_response.text
        except Exception as e:
            return f"Error generating final meeting minutes: {str(e)}"

if __name__ == "__main__":
    with open("transcript.txt", 'r') as file:
        transcript = file.read()
    try:
        # Initialize the generator
        generator = MeetingMinutesGenerator()
        # Generate meeting minutes
        minutes = generator.generate(transcript)
        print("\nGenerated Meeting Minutes:\n")
        print(minutes)
    except Exception as e:
        print(f"Error: {str(e)}")
