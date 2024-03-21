import { useContext } from "react"
import { MapContext } from "../context/map"
import './InfoCanvas.css'
import { useFilters } from "../hooks/useFilters.js"

export function InfoCanvas(){
    const { markers } = useContext(MapContext)
    const {timeToPrevious} = useFilters()
    const time = timeToPrevious(markers, 'DRONE')
    
    return (
        <section className="meas-info">
        <h1>Useful info from measurements perspective</h1>
        <table className="table-info">
                <thead>
                    <tr>
                        <th className="table-labels">ID</th>
                        <th className="table-labels">Latitude</th>
                        <th className="table-labels">Longitude</th>
                        <th className="table-labels">Distance</th>
                        <th className="table-labels">Time</th>
                    </tr>
                </thead>
                <tbody>
                {
                    markers.map((entry, cnt) =>{
                        return (
                            <tr key={cnt}>
                                <td>{entry.id}</td>
                                <td>{entry.lat.toFixed(5)}</td>
                                <td>{entry.lng.toFixed(5)}</td>
                                <td>{entry.distToPrevious.toFixed(5)}</td>
                                <td>{time[cnt].toFixed(5)}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
        </table>
        </section>
    )
}