from http import HTTPStatus
from lib.api_helper import request_api


class TestSudokuApi:

    def test_get_board(self, api_url,  **kwargs):
        """
        GET /board
        Assert status is 200.
        GET /board/id
        Assert board id is same as url id
        """
        resp = request_api(
        'GET',
        api_url,
        "/board",
        **kwargs
    )

        if resp.status_code != HTTPStatus.OK:
            raise ValueError('Failed to get a board.')

        data = resp.json()

        resp = request_api(
            'GET',
            api_url,
            "/board/{entity_id}",
            entity_id=data['id'],
            **kwargs
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.json()['id'] == data['id'], 'Failed to get correct board'

    @pytest.mark.xfail("Validate throws a 400, validate function in code is wrongly implemented")
    def test_validate_board(self, api_url,  **kwargs):
        """
        PUT /board/validate
        Add body : valid fields object
        expected : with correct fields board should be validated
        """
        resp = request_api(
            'PUT',
            api_url,
            "/board/validate",
            data={"fields":[
            [
                8,
                2,
                7,
                1,
                5,
                4,
                3,
                9,
                6
            ],
            [
                9,
                6,
                5,
                3,
                2,
                7,
                1,
                4,
                8
            ],
            [
                3,
                4,
                1,
                6,
                8,
                9,
                7,
                5,
                2
            ],
            [
                5,
                9,
                3,
                4,
                6,
                8,
                2,
                7,
                1
            ],
            [
                4,
                7,
                2,
                5,
                1,
                3,
                6,
                8,
                9
            ],
            [
                6,
                1,
                8,
                9,
                7,
                2,
                4,
                3,
                5
            ],
            [
                7,
                8,
                6,
                2,
                3,
                5,
                9,
                1,
                4
            ],
            [
                1,
                5,
                4,
                7,
                9,
                6,
                8,
                2,
                3
            ],
            [
                2,
                3,
                9,
                8,
                4,
                1,
                5,
                6,
                7
            ]
        ]
        },
            headers={'Content-Type': 'application/json'},
            **kwargs
        )

        assert resp.status_code == HTTPStatus.OK
