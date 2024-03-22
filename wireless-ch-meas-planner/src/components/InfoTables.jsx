import { useContext } from 'react'
import { DroneMarkersContext } from '../context/dronemarkers.jsx'
import { GroundMarkersContext } from '../context/groundmarkers.jsx'
import { useFilters } from "../hooks/useFilters.js"
import './InfoTables.css'

export function InfoTableDrone (){
    const { markers } = useContext(DroneMarkersContext)
    const {timeToPrevious} = useFilters()
    const time = timeToPrevious(markers, 'DRONE')
    
    return (
        <table className="table-info" id="table-drone">
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
                                <td>{entry.distToPrevious.toFixed(1)}</td>
                                <td>{time[cnt].toFixed(2)}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
        </table>
    )
}

export function InfoTableGround (){
    const { gndmarkers } = useContext(GroundMarkersContext)
    const {timeToPrevious} = useFilters()
    const time = timeToPrevious(gndmarkers, 'GROUND')
    
    return (
        <table className="table-info" id="table-ground">
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
                    gndmarkers.map((entry, cnt) =>{
                        return (
                            <tr key={cnt}>
                                <td>{entry.id}</td>
                                <td>{entry.lat.toFixed(5)}</td>
                                <td>{entry.lng.toFixed(5)}</td>
                                <td>{entry.distToPrevious.toFixed(1)}</td>
                                <td>{time[cnt].toFixed(2)}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
        </table>
    )
}