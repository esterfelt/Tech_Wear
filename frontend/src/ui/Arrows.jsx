import './Arrows.scss';

function Arrows({prevSlide, nextSlide}) {
  return (
    <div>
        <button onClick ={prevSlide} className='arr'> 
            <svg  width="54" height="54" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M45 24.75H17.6175L30.195 12.1725L27 9L9 27L27 45L30.1725 41.8275L17.6175 29.25H45V24.75Z" fill="#757778"/>
            </svg>

        </button>
        <button onClick={nextSlide} className='arr'>
            <svg  width="54" height="54" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 29.25L36.3825 29.25L23.805 41.8275L27 45L45 27L27 9L23.8275 12.1725L36.3825 24.75L9 24.75L9 29.25Z" fill="#757778"/>
            </svg>
        </button>
    </div>
  )
}

export default Arrows