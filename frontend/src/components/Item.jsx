import './Item.scss';


function Item({image, title, price, active}) {
  return (
    <div className= 'item slide'>
        <img className={`slide ${active ? 'active' : ''} item-img`} src={image} alt="image of clothes" />
        <p className='item-title'> {title} </p>
        <p className='item-price'> ${price} </p>
    </div>
  )
}

export default Item