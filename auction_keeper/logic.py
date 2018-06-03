# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2018 reverendus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from threading import RLock
from typing import Optional

from auction_keeper.risk_model import ModelFactory, Model, ModelOutput, ModelParameters, ModelInput


class Auction:
    def __init__(self, id: int, model: Model):
        assert(isinstance(id, int))

        self.output = None
        self.output_lock = RLock()
        self.model = None
        self.transaction = None
        self.transaction_price = None

        self.model = model

        #TODO these two will ultimately go away
        self.price = None
        self.gas_price = None

        #TODO we will implement locking later
        self.lock = RLock()

    def update_output(self, output: ModelInput):
        assert(isinstance(output, ModelInput))

        with self.output_lock:
            self.output = output
        print(self.output)

    def model_output(self) -> Optional[ModelOutput]:
        return self.model.output()

    def remove(self):
        self.model.stop()


class Auctions:
    def __init__(self, model_factory: ModelFactory):
        assert(isinstance(model_factory, ModelFactory))

        self.auctions = {}
        self.model_factory = model_factory

    def get_auction(self, id: int):
        assert(isinstance(id, int))

        if id not in self.auctions:
            # Start the model
            model_parameters = ModelParameters(id=id)

            model = self.model_factory.create_model()
            model.start(model_parameters)

            # Register new auction
            self.auctions[id] = Auction(id, model)

        return self.auctions[id]

    def remove_auction(self, id: int):
        assert(isinstance(id, int))

        # Stop the model
        self.auctions[id].model.stop()

        # Remove the auction
        del self.auctions[id]