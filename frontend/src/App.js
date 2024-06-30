import logo from './logo.svg';
import './App.css';
import {useEffect, useState} from "react";

function App() {

  const [ingressText, setIngressText] = useState("");
  const [altheaText, setAltheaText] = useState("");
  const [ogQuestion, setOgQuestion] = useState("");
  const [waitingForFinalInteraction, setWaitingForFinalInteraction] = useState(false);
  const [altheaOutput, setAltheaOutput] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [scriptedOutput, setScriptedOutput] = useState("");
  const [patientKnowledge, setPatientKnowledge] = useState("");

    useEffect(() => {
        const requestOptions = {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            }
        };
        fetch(`${process.env.REACT_APP_BACKEND_BASE_URL}/patient_info`, requestOptions)
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                setPatientKnowledge(data.knowledge);
            });
    }, []);

  useEffect(() => {
    const requestOptions = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        username: "username",
        password: "password",
      }),
    };
    fetch(`${process.env.REACT_APP_BACKEND_BASE_URL}/login`, requestOptions)
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
    });
  }, []);

  function sendIngressText(event) {
    event.preventDefault();
    const requestOptions = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        text: ingressText,
      }),
    };
    setIngressText("");
    setIsLoading(true)
    fetch(`${process.env.REACT_APP_BACKEND_BASE_URL}/text_ingress`, requestOptions)
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setIsLoading(false)
      });
  }

  function sendAltheaText(event) {
    event.preventDefault();
    setIsLoading(true);
    if (waitingForFinalInteraction) {
        sendAltheaFinalInteraction();
        return;
    }
    const requestOptions = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        text: altheaText,
      }),
    };
    setAltheaText("");
    fetch(`${process.env.REACT_APP_BACKEND_BASE_URL}/ask_althea`, requestOptions)
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setIsLoading(false);
        setWaitingForFinalInteraction(true);
        setAltheaOutput(data.followupQuestions);
        setScriptedOutput("Cool, I can help, I just need to know a few more things.");
        setOgQuestion(altheaText);
      });
  }

  function sendAltheaFinalInteraction() {
    const requestOptions = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        text: ogQuestion,
        user_info: altheaText
      }),
    };
    setAltheaText("");
    fetch(`${process.env.REACT_APP_BACKEND_BASE_URL}/ask_althea_final_interaction`, requestOptions)
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setIsLoading(false);
        setWaitingForFinalInteraction(false);
        setAltheaOutput(data.tasks);
        setScriptedOutput("Got it, so here's what we will need to do.");
      });
  }

  let ingressForm = (
    <form className="ingress_form" onSubmit={(event) => sendIngressText(event)}>
      <input
        type="text"
        placeholder="Tell me any information you want me to remember..."
        value={ingressText}
        onChange={(event) => setIngressText(event.target.value)}
      />
      <button className="landingPage__button" type="submit">
        SEND
      </button>
      <div className="patientInfoHeader">
            <p>Knowledge about</p>
            <h3 className="name">You.</h3>
        </div>
        <p className="patientInfo">{patientKnowledge}</p>
    </form>
  );

  let altheaForm = (
    <form className="ingress_form" onSubmit={(event) => sendAltheaText(event)}>
      <h6>I'll recall your information to help you navigate healthcare.</h6>
        <input
        type="text"
        placeholder="How can I help you navigate healthcare today?"
        value={altheaText}
        onChange={(event) => setAltheaText(event.target.value)}
      />
      <button className="landingPage__button" type="submit">
        SEND
      </button>
    </form>
  );

  return (
    <div className="app">
      <div className="wrapper">
        <h2 className="title">Althea.</h2>
        {ingressForm}
        {isLoading ? <div className="loading-bar"></div> : <p className="scripted">{scriptedOutput}</p>}
        <ol key={altheaOutput.join()}>
          {altheaOutput.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ol>
        {altheaForm}
      </div>
    </div>
  );
}

export default App;
