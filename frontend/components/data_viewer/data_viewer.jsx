import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class DataViewer extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            allDataNames: [],
        };

        // bind methods
        this.getData = this.getData.bind(this);
    }

    getData(name) {
        // Request default data
        $.ajax({
            url: '/data/' + name,
            method: 'GET',
            success: (response) => {
                console.log(response.data);
            }
        })
    }

    componentDidMount() {
        // Request default data
        $.ajax({
            url: '/all_data_names',
            method: 'GET',
            success: (response) => {
                this.setState({
                    allDataNames: response.names
                });
            }
        });

        this.getData('US CPI NSA');
    }

    render() {


        return (
            <Container fluid>
                <Row>
                    This is the DataViewer.
                </Row>
            </Container>
        );
    }

}

export default DataViewer;

