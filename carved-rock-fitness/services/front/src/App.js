import React from 'react';
import './App.css';
import axios from 'axios'


const workouts = [
    "running",
    "swimming",
    "jumping",
];

const successMessage = (score, workout_id) => ({
    text: `You've scored ${score} on workout ${workout_id}`,
})

const failureMessage = () => ({
    text: `Something went wrong :C`,
})

class App extends React.Component
{
    constructor(){
        super();

        this.state = {
            workout: workouts[0],
            begin: 0,
            end: 1,
            intensity: 25,
            message: {
                text: "",
            },
        };
    }

    handleKindChange(event)
    {
        this.setState({
          workout: event.target.value,
        })
    }

    handleBeginChange(event)
    {
        this.setState({
          begin: event.target.value,
        })
    }

    handleEndChange(event)
    {
        this.setState({
          end: event.target.value,
        })
    }

    handleIntensityChange(event)
    {
        this.setState({
          intensity: event.target.value,
        })
    }

    async submitWorkout(event)
    {
        event.preventDefault();

        const form = event.target // button
            .parentNode // .form-group
            .parentNode

        this.setState({
            message: {text: ""},
        })

        form.reset();

        const backend_url = process.env.REACT_APP_BACKEND_URL || "/backend";

        let r;

        try {
            r = await axios.post(backend_url, {
              kind: this.state.workout,
              begin: this.state.begin,
              end: this.state.end,
              intensity: this.state.intensity,
            });
        }
        catch(e) {
            this.setState({
              message: failureMessage(),
            })
            return
        }

        const { data } = r;
        const { score, workout_id } = data;

        this.setState({
          message: successMessage(score, workout_id),
        })
    }

    render()
    {
        return (
            <div className="App">
                <div className="msg">
                    { this.state.message.text }
                </div>
                <header className="App-header">
                    <form>
                        <div className="form-group">
                        workout kind
                        <select className="form-control form-control-lg" onChange={this.handleKindChange.bind(this)}>
                            {workouts.map((workout, index) =>
                                <option value={workout} key={index}>{workout}</option>
                            )}
                        </select>

                        begin
                        <input type="number" className="form-control" step="1" min="0" size="2" max="24" onChange={this.handleBeginChange.bind(this)} required/>
                        end
                        <input type="number" className="form-control" step="1" min="0" size="2" max="24" required onChange={this.handleEndChange.bind(this)}/>
                        intensity
                        <input type="number" className="form-control" step="1" min="0" size="3" max="100" required onChange={this.handleIntensityChange.bind(this)}/>

                        <button className="btn btn-default" onClick={this.submitWorkout.bind(this)}>submit</button>
                        </div>
                    </form>
                </header>
            </div>
        );
    }
}

export default App;
