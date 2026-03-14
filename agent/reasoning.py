import os
import time
from google import genai
from langchain_core.prompts import PromptTemplate

# Hardcoded fallback key from user
FALLBACK_KEY = "AIzaSyBLrCiaFOS0YtbcsQwyUNw9W8MwZ9e8TqQ"

def explain_decision(date, price, prob, indicators):
    """
    Uses LLM to explain WHY the model thinks the stock is going up.
    """
    api_key = os.getenv("GEMINI_API_KEY") or FALLBACK_KEY
    
    if not api_key:
        print("\n[!] GEMINI_API_KEY not found. Using MOCK explanation.")
        return mock_explanation(date, price, prob, indicators)

    try:
        client = genai.Client(api_key=api_key)
        
        template = """
        You are a senior hedge fund analyst. 
        Our quantitative model has flagged a BUY signal for AAPL.
        
        Date: {date}
        Price: ${price:.2f}
        Model Confidence: {prob:.1%} (Threshold is 60%)
        
        Technical Indicators:
        - RSI (14): {rsi:.2f} (Overbought > 70, Oversold < 30)
        - MACD: {macd:.4f}
        - SMA (50): ${sma:.2f}
        - Volume Trend (OBV): {obv:.0f}
        
        Task:
        Explain WHY this is a good trade based on the indicators. 
        Be professional, concise, and persuasive.
        """
        
        prompt = PromptTemplate(
            input_variables=["date", "price", "prob", "rsi", "macd", "sma", "obv"],
            template=template
        )
        
        final_prompt = prompt.format(
            date=date,
            price=price,
            prob=prob,
            rsi=indicators.get('rsi', 0),
            macd=indicators.get('macd', 0),
            sma=indicators.get('sma_50', 0),
            obv=indicators.get('obv', 0)
        )
        
        # Retry Logic for Rate Limits (CRITICAL for Free Tier)
        # using gemini-2.5-flash as per user documentation
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=final_prompt,
                )
                return response.text
                
            except Exception as e:
                error_str = str(e)
                # Rate limit error usually contains 429
                if "429" in error_str:
                    wait_time = 30 # Google Free Tier often asks for ~25s wait
                    print(f"\n[!] Rate Limit Hit (429). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise e

    except Exception as e:
        print(f"\n[!] API Error: {str(e)}")
        print("[*] Falling back to Mock Analyst...")
        return mock_explanation(date, price, prob, indicators)

def mock_explanation(date, price, prob, indicators):
    return f"""
    [MOCK AI EXPLANATION] 
    Date: {date} | Price: ${price:.2f}
    The model is {prob:.1%} confident.
    RSI is {indicators.get('rsi'):.2f}, suggesting momentum.
    (Add GEMINI_API_KEY to see real reasoning)
    """
