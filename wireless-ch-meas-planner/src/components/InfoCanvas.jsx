import './InfoCanvas.css'
import { InfoTableDrone, InfoTableGround } from "./InfoTables.jsx"

export function InfoCanvas(){
    return (
        <section className="meas-info">
            <div className='drone-info'>
                <h1>Drone info</h1>
                <InfoTableDrone></InfoTableDrone>
            </div>
            <div className='ground-info'>
                <h1>Ground info</h1>
                <InfoTableGround></InfoTableGround>
            </div>
        </section>
    )
}