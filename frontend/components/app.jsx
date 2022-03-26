import React from 'react';
import { Route } from 'react-router-dom';

import Footer from './footer/footer_container';

export default () => (
    <div>
        <Route path="/" component={Footer} />
    </div>
);
