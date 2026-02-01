"""AI-powered job matching engine."""

import os
from typing import Dict, List
import anthropic
import openai


class JobMatcher:
    """AI-powered job matching and scoring."""

    def __init__(self, user_profile: Dict, resume_data: Dict):
        """Initialize matcher with user profile and resume data."""
        self.user_profile = user_profile
        self.resume_data = resume_data

        # Initialize AI clients
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')

        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            self.ai_provider = 'anthropic'
        elif self.openai_key:
            openai.api_key = self.openai_key
            self.ai_provider = 'openai'
        else:
            raise ValueError("No AI API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")

    def score_job(self, job: Dict) -> tuple[float, str]:
        """
        Score a job against user profile.

        Returns:
            tuple: (score 0-100, reasoning text)
        """
        prompt = self._build_matching_prompt(job)

        if self.ai_provider == 'anthropic':
            return self._score_with_anthropic(prompt)
        else:
            return self._score_with_openai(prompt)

    def score_jobs_batch(self, jobs: List[Dict]) -> List[Dict]:
        """Score multiple jobs."""
        scored_jobs = []

        for i, job in enumerate(jobs, 1):
            try:
                score, reasoning = self.score_job(job)
                job['match_score'] = score
                job['match_reasoning'] = reasoning
                scored_jobs.append(job)

                if i % 10 == 0:
                    print(f"Scored {i}/{len(jobs)} jobs...")

            except Exception as e:
                print(f"Error scoring job {job.get('title', 'Unknown')}: {e}")
                job['match_score'] = 0
                job['match_reasoning'] = f"Error: {str(e)}"
                scored_jobs.append(job)

        return scored_jobs

    def _build_matching_prompt(self, job: Dict) -> str:
        """Build prompt for AI job matching."""
        # Extract key info from resume data
        skills = self.resume_data.get('skills', [])
        companies = self.resume_data.get('companies', [])
        keywords = self.resume_data.get('keywords', [])

        prompt = f"""You are an expert career advisor helping a Principal Product Manager evaluate job opportunities.

USER PROFILE:
- Name: {self.user_profile.get('name', 'Jim Rome')}
- Current Role: {self.user_profile.get('current_role', 'Principal Product Manager')}
- Years of Experience: {self.user_profile.get('years_experience', '15')} years
- Minimum Salary Requirement: $175,000+
- Skills: {', '.join(skills[:20])}
- Previous Companies: {', '.join(companies)}
- Key Strengths: AI/ML, Mobile Products, Fintech, Real Estate Tech, Consumer Products

TARGET JOB:
- Title: {job.get('title', 'Unknown')}
- Company: {job.get('company', 'Unknown')}
- Location: {job.get('location', 'Unknown')}
- Description: {job.get('description', '')[:1500]}
- Salary Range: {job.get('salary_min', 'Not specified')}-{job.get('salary_max', 'Not specified')}

EVALUATION CRITERIA:
1. Role Seniority Match (25 points): Is this Principal/Director/VP level?
2. Skills Alignment (25 points): Match with AI, mobile, product management expertise
3. Industry Fit (20 points): Fintech, real estate, consumer tech, marketplace
4. Company Quality (15 points): Growth stage, reputation, impact potential
5. Salary & Location (15 points): $175k+ salary requirement; Manhattan/Bronx/Remote preferred

IMPORTANT: If salary is listed and is below $175,000, score should be significantly lower (max 60).

Provide:
1. A score from 0-100
2. Brief reasoning (2-3 sentences) explaining the score

Format your response exactly as:
SCORE: [number]
REASONING: [your explanation]
"""
        return prompt

    def _score_with_anthropic(self, prompt: str) -> tuple[float, str]:
        """Score job using Anthropic Claude."""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response = message.content[0].text
            return self._parse_score_response(response)

        except Exception as e:
            print(f"Anthropic API error: {e}")
            return 0, f"Error: {str(e)}"

    def _score_with_openai(self, prompt: str) -> tuple[float, str]:
        """Score job using OpenAI GPT."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3,
            )

            response_text = response.choices[0].message.content
            return self._parse_score_response(response_text)

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return 0, f"Error: {str(e)}"

    def _parse_score_response(self, response: str) -> tuple[float, str]:
        """Parse score and reasoning from AI response."""
        try:
            # Extract score
            score_line = [line for line in response.split('\n') if 'SCORE:' in line][0]
            score = float(score_line.split('SCORE:')[1].strip().split()[0])

            # Extract reasoning
            reasoning_line = [line for line in response.split('\n') if 'REASONING:' in line]
            if reasoning_line:
                reasoning = reasoning_line[0].split('REASONING:')[1].strip()
            else:
                # Fallback: use everything after score
                reasoning = response.split(score_line)[1].strip()

            return score, reasoning

        except Exception as e:
            print(f"Error parsing response: {e}")
            # Fallback: return moderate score with full response
            return 50, response

    def generate_cover_letter(self, job: Dict) -> str:
        """Generate a tailored cover letter for a job."""
        prompt = f"""Generate a concise, professional cover letter for this job application.

USER:
- Name: {self.user_profile.get('name', 'Jim Rome')}
- Current Role: Principal Product Manager at Realtor.com
- Experience: 15 years in product management
- Key Achievements:
  * Led AI-powered search experiences driving 15% revenue growth
  * Scaled mobile products to millions of users
  * Expert in fintech and real estate technology

JOB:
- Title: {job.get('title')}
- Company: {job.get('company')}
- Description: {job.get('description', '')[:800]}

Write a 3-paragraph cover letter that:
1. Opens with enthusiasm and key qualification match
2. Highlights 2-3 most relevant achievements
3. Closes with call to action

Keep it under 250 words. Be confident but not arrogant.
"""

        if self.ai_provider == 'anthropic':
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional cover letter writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
            )
            return response.choices[0].message.content

    def identify_key_gaps(self, job: Dict) -> List[str]:
        """Identify skill/experience gaps for a job."""
        prompt = f"""Analyze this job posting and identify any skill or experience gaps for the candidate.

CANDIDATE SKILLS: {', '.join(self.resume_data.get('skills', [])[:20])}

JOB REQUIREMENTS: {job.get('description', '')[:1000]}

List 3-5 potential gaps or areas where the candidate might need to emphasize learning/experience.
Be realistic - list actual gaps, not just minor differences.

Format as a bullet list.
"""

        if self.ai_provider == 'anthropic':
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            response = message.content[0].text
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            response = response.choices[0].message.content

        # Parse bullet points
        gaps = [line.strip('- •*').strip() for line in response.split('\n') if line.strip()]
        return gaps[:5]
