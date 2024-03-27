import './MapLegends.css'

export function MapLegends () {
    return (
            <section className='legends-info'>
                <div className='legends-info-item'>
                    <strong>Flight Geography</strong>
                    <svg  xmlns="http://www.w3.org/2000/svg" className='img-info-item' id='fg-item' viewBox="0 0 1 1" width='1rem' height='1rem'></svg>
                </div>
                <div className='legends-info-item'>
                    <strong>Contingency Volume</strong>
                    <svg  xmlns="http://www.w3.org/2000/svg" className='img-info-item' id='cv-item' viewBox="0 0 1 1" width='1rem' height='1rem'></svg>
                </div>
                <div className='legends-info-item'>
                    <strong>Ground Risk Buffer</strong>
                    <svg  xmlns="http://www.w3.org/2000/svg" className='img-info-item' id='grb-item' viewBox="0 0 1 1" width='1rem' height='1rem'></svg>
                </div>
                <div className='legends-info-item'>
                    <strong>Drone location</strong>
                    <img className='img-info-item' id='dl-item' alt='DL' src='/drone-marker.png' />
                </div>
                <div className='legends-info-item'>
                    <strong>Ground location</strong>
                    <svg  xmlns="http://www.w3.org/2000/svg" className='img-info-item' id='gl-item' viewBox="0 0 1 1" width='1rem' height='1rem'></svg>
                </div>
                <div className='legends-info-item'>
                    <strong>Drone route</strong>
                    <svg  xmlns="http://www.w3.org/2000/svg" className='img-info-item' id='dr-item' viewBox="0 0 1 1" width='1rem' height='1rem'></svg>
                </div>
                <div className='legends-info-item'>
                    <strong>Drone gimbal yaw</strong>
                    <svg  xmlns="http://www.w3.org/2000/svg" className='img-info-item' id='dgyaw-item' viewBox="0 0 1 1" width='1rem' height='1rem'></svg>
                </div>
        </section>
    )
}