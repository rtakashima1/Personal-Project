import React, {useState,useEffect} from 'react';
import FlashcardList from './FlashcardList';
import './app.css'
import axios from 'axios'

function App() {
  const [flashcards, setFlashcards] = useState(SAMPLE_FLASHCARDS)

useEffect(() => {
  axios
    .get('https://opentdb.com/api.php?amount=10')
    .then(res => {
      setFlashcards(res.data.results.map((questionItem,index) => {
        const answer = decodeString(questionItem.correct_answer)
        const options = [...questionItem.incorrect_answers.map(a => decodeString(a)),answer]
        return {
          id: `${index}-${Date.now()}`,
          question: decodeString(questionItem.question),
          answer: answer,
          options: options.sort(() => Math.random() - .5)
        }
      }))
    })
}, [])

  function decodeString(str) {
    const textArea = document.createElement('textarea')
    textArea.innerHTML= str
    return textArea.value
  }

  return (
    <div className="container">
      <FlashcardList flashcards = {flashcards} />
    </div>
  );
}

const SAMPLE_FLASHCARDS = [
{
  id: 1,
  question: 'what is 2 + 2?',
  answer: '4', 
  options: [
    '2', 
    '3',
    '4',
    '5'
  
  ]
},
{
  id: 2,
  question: 'What is the powerhouse of the cell?',
  answer: 'mitochondria', 
  options: [
    'mitochondria', 
    'ribosomes',
    'nucleus',
    'golgi bodies'
  ]
},
{
  id: 3,
  question: 'It is much easier for a small animal to run uphill than for a larger animal, because',
  answer: 'smaller animals have a higher metabilic rate', 
  options: [
    'it is easier to carry small body weight', 
    'smaller animals have a higher metabilic rate',
    'small animals have a lower O2 requirement',
    'the efficiency of muscles in large animals is less than in the small animals'
  ]
}



]


export default App;
