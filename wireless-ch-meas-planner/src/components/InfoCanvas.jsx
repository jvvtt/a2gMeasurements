import { useContext } from "react"
import { MapContext } from "../context/map"
import './InfoCanvas.css'

const gnd_speeds = ["10km/h", "20km/h", "30km/h"]
const drone_speeds = ["0.5m/s", "1m/s", "2m/s", "3m/s"]

export function InfoCanvas(){

    const {markers} = useContext(MapContext)

    return (
        <main>
            <div className="speed-selector">
                { gnd_speeds.map((entry, cnt)=> {
                    return (
                        <button key={cnt}>{`Vg = ${entry}`}</button>        
                    )
                })                
                }
                {
                  drone_speeds.map((entry, cnt)=> {
                    return (
                        <button key={cnt}>{`Vd = ${entry}`}</button>        
                    )
                })  
                }
            </div>
            <ul>
            {markers.map((entry,cnt) => {
                return (
                    <li key={cnt}>
                        <strong>{entry.lat}, {entry.lng}, {entry.id}</strong>
                    </li>
                )
            })}
            </ul>
        </main>        
    )
}