import { useContext, useId } from "react"
import { MapContext } from "../context/map"
import {gnd_speeds, drone_speeds, decimal_places} from '../constants/constants.js'
import './InfoCanvas.css'

const handleGndSpeed = (e) => {    
    const gnd_speed_sel_labels = document.querySelectorAll('.gnd-speed-selector label');
    console.log(gnd_speed_sel_labels);
    gnd_speed_sel_labels.forEach(label=> {
        label.style.backgroundColor = 'rgb(255, 109, 25)'
    });
    e.target.labels[0].style.backgroundColor = 'rgb(255, 171, 123)'
}

const handleDroneSpeed = (e) => {
    document.querySelectorAll('.drone-speed-button').forEach(entry=>{
         entry.style.backgroundColor = 'rgb(18, 80, 36);'
         console.log(entry)
    }) 
    e.target.style.backgroundColor = 'rgb(47, 139, 73)'
}

export function InfoCanvas(){
    const gndSpeedSelId = useId()
    const droneSpeedSelId = useId()

    const {markers} = useContext(MapContext)

    return (
        <main>
            <div className="speed-selector">
                { gnd_speeds.map((entry, cnt)=> {
                    return (
                        <div key={cnt} className="gnd-speed-selector">
                            <input type="radio" id={`${cnt}${gndSpeedSelId}`} onInput={(e)=>handleGndSpeed(e)}/>
                            <label id={`${cnt}${gndSpeedSelId}`}
                                   htmlFor={`${cnt}${gndSpeedSelId}`}>{`Vg = ${entry}`}</label>
                        </div>
                    )
                })                
                }
                {
                  drone_speeds.map((entry, cnt)=> {
                    return (
                            <button key={cnt} 
                                    className="drone-speed-button"
                                    onClick={(e)=>handleDroneSpeed(e)}>
                                        {`Vd = ${entry}`}
                            </button>
                    )
                })  
                }
            </div>
            <div className="marker-labels">
                <strong>ID</strong>
                <strong>Latitude</strong> 
                <strong>Longitude</strong>  
                <strong>Distance</strong>              
            </div>
            <ul>            
            {markers.map((entry,cnt) => {
                return (
                    <li className="marker-values" key={cnt}>
                        <strong>{entry.id}</strong>
                        <strong>{entry.lat.toFixed(5)}</strong> 
                        <strong>{entry.lng.toFixed(5)}</strong>                            
                        <strong>{entry.distToPrevious.toFixed(5)}</strong>
                    </li>
                )
            })}
            </ul>
        </main>        
    )
}