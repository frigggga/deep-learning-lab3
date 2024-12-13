import requests
import json
import matplotlib.pyplot as plt


def fetch_llm_response(ques):
    url = 'http://localhost:11434/api/generate'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gemma",  # change model here
        "prompt": ques,
        "stream": False,
    }
    response = requests.post(url, headers=headers, json=data)
    res = response.json()['response']
    print(res)
    return res


def detect_yes_no(response):
    if "[Yes]" in response:
        return "yes"
    elif "[No]" in response:
        return "no"
    else:
        return "error"


def score_response(response, correct_answer):
    score = 0

    # Check understanding of the problem
    if "prime number" in response:
        score += 1  # Correctly identifies the task

    # Check initial divisibility checks
    if "dividing by 2" in response or "divisibility by small primes" in response:
        score += 1

    # Check edge cases handling
    if "odd" in response:
        score += 1

    # Check edge cases handling
    if "even" in response:
        score += 1

    # Check edge cases handling
    if "square root" in response:
        score += 1

    if "remainder" in response:
        score += 1

    # Check formatting and clarity
    if response.strip().count("\n") > 3:  # At least structured in paragraphs/steps
        score += 2

    # Check factorization or higher tests
    if "factored" in response or "prime factorization" in response:
        score += 2

    # Check conclusion alignment
    if detect_yes_no(response) == correct_answer:
        score += 5

    return score


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('questions.json', 'r') as file:
        questions = json.load(file)

    # Load the answers from JSON file
    with open('answers.json', 'r') as file:
        answers = json.load(file)

    # Map answers to a dictionary for easy lookup
    answers_dict = {int(item['_id']): item['answer'] for item in answers}
    # Compare LLM responses with correct answers
    results = []
    scores = []
    correct_count = 0
    total_questions = len(questions)
    response_analysis = []

    for question in questions:
        question_id = int(question['_id'])
        query = question['query']
        correct_answer = answers_dict.get(question_id, "")

        # Fetch LLM response
        try:
            llm_response = fetch_llm_response(query)
            is_correct = (detect_yes_no(llm_response) == correct_answer)
            correct_count += is_correct
            score = score_response(llm_response, correct_answer)
            scores.append(score)

            # Record analysis
            response_analysis.append({
                "id": question_id,
                "query": query,
                "llm_response": llm_response,
                "correct_answer": correct_answer,
                "score": score,
                "is_correct": is_correct
            })

        except Exception as e:
            scores.append(0)
            response_analysis.append({
                "id": question_id,
                "query": query,
                "llm_response": "Error",
                "correct_answer": correct_answer,
                "score": 0,
                "is_correct": False
            })

    # Calculate accuracy
    accuracy = (correct_count / total_questions) * 100
    print(accuracy)

    # Prepare data for plotting
    correct_responses = [1 if item['is_correct'] else 0 for item in response_analysis]
    question_ids = [item['id'] for item in response_analysis]

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.plot(question_ids, correct_responses, marker='o', linestyle='-', label='Correct Responses')
    plt.xlabel('Question ID')
    plt.ylabel('Correct (1) or Incorrect (0)')
    plt.title(f'LLM Response Analysis (Accuracy: {accuracy:.2f}%)')
    plt.legend()
    plt.grid()
    # Save the plot to a file
    output_file = "llm_scores_plot1.png"  # Change file name and extension as needed
    plt.savefig(output_file, dpi=300, bbox_inches='tight')  # High-quality image
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(range(1, len(scores) + 1), scores, marker='o', linestyle='-', label='Scores')
    plt.title("LLM Response Score Trends")
    plt.xlabel("Question Number")
    plt.ylabel("Score")
    plt.xticks(range(0, len(scores) + 1, max(1, len(scores) // 10)))  # Adjust x-axis ticks dynamically
    plt.legend()
    plt.grid()
    # Save the plot to a file
    output_file = "llm_scores_plot2.png"  # Change file name and extension as needed
    plt.savefig(output_file, dpi=300, bbox_inches='tight')  # High-quality image
    plt.show()
