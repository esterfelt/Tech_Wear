import "./NewCollection.scss";

import Item from "./Item";
import { data } from "../utils/data";

function NewCollection() {
  return (
    <div className="container">
      <div className="new">
        <h3 className="header">/new collection</h3>
        <div className="new-items">
          {data.slice(0, 4).map((item, index) => (
            <Item
              key={index}
              image={item.image}
              title={item.title}
              price={item.price}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default NewCollection;
