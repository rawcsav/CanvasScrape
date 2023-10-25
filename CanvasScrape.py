import os
import argparse
import itertools
import csv
from bs4 import BeautifulSoup


def extract_data_from_soup(soup):
    """Extract questions, answers, and the correct answer from a BeautifulSoup object."""
    questions = [div.get_text(strip=True) for div in soup.select('div.question_text')]
    extracted_data = []
    answers_divs = soup.select('div.answers')
    for q, ans_div in zip(questions, answers_divs):
        answers = [div.get_text(strip=True) for div in
                   ans_div.select('div.answer_text')]
        correct_answers = [div.get_text(strip=True) for div in
                           ans_div.select('div.answer.correct_answer div.answer_text')]
        correct_answer = correct_answers[0] if correct_answers else None
        extracted_data.append({
            "question": q,
            "answers": answers,
            "correct_answer": correct_answer
        })
    return extracted_data


def remove_duplicates(extracted_data):
    # Convert data to tuple form for hashing in a set
    unique_data = set(
        (data['question'], tuple(data['answers']), data['correct_answer'])
        for data in extracted_data
    )
    # Convert back to original format
    return [{"question": q, "answers": list(choices), "correct_answer": correct_answer}
            for q, choices, correct_answer in unique_data]


def save_to_txt(output_filepath, extracted_data):
    with open(output_filepath, 'w', encoding="utf-8") as output_file:
        for data in extracted_data:
            output_file.write(f"Question: {data['question']}\n")
            for ans in data['answers']:
                output_file.write(f" - {ans}\n")
            output_file.write(f"Correct Answer: {data['correct_answer']}\n\n")
        output_file.write("\n\n")
    print(f"Data saved to: {output_filepath}")


def save_to_csv(output_filepath, extracted_data):
    quizlet_formatted_data = [
        {
            "term": data['question'] + "\n" + "\n".join(data['answers']),
            "definition": data['correct_answer']
        }
        for data in extracted_data
    ]

    with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['term', 'definition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in quizlet_formatted_data:
            writer.writerow(entry)

    print(f"Data saved to: {output_filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract questions, answers, and the correct answer from HTML files.')
    parser.add_argument('filepaths', metavar='F', type=str, nargs='*', default=[],
                        help='a path to the HTML file to process')
    parser.add_argument('-o', '--output', type=str,
                        help='Output directory where the result should be saved')
    args = parser.parse_args()

    if not args.filepaths:
        print("Welcome to the CanvasScrape Tool!")
        print("Please provide the file paths of the HTML files you want to process.")
        print("You can provide multiple file paths separated by spaces or commas.")
        print("Press Enter when done.")

        user_input = input("Enter file paths: ").strip()
        filepaths = [fp.strip() for fp in user_input.replace(',', ' ').split()]
    else:
        filepaths = args.filepaths

    if args.output:
        base_output_filepath = args.output
    else:
        print("\nWhere would you like to save the extracted questions and answers?")
        print(
            "Provide a directory to save with the default filename or specify a full path excluding file extension.")
        base_output_filepath = input(
            "Output base path (default is current directory): ").strip()
        if not base_output_filepath:
            base_output_filepath = "extracted_questions_and_answers"

    extracted_data = []
    for filepath in filepaths:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        extracted_data.extend(extract_data_from_soup(soup))

    user_response = input(
        "\nWould you like to remove duplicates? (yes/no): ").strip().lower()
    if user_response in ['yes', 'y']:
        extracted_data = remove_duplicates(extracted_data)

    user_response = input(
        "\nWhich format would you like to save the data in? (txt/csv): ").strip().lower()

    if user_response == "txt":
        output_filepath = base_output_filepath + ".txt"
        save_to_txt(output_filepath, extracted_data)
    elif user_response == "csv":
        output_filepath = base_output_filepath + ".csv"
        save_to_csv(output_filepath, extracted_data)

    print(f"\nData saved to: {output_filepath}")


if __name__ == "__main__":
    main()

