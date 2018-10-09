import math as m
import matplotlib.pyplot as plt
import torch
from utils import TimeIt

device = torch.device("cuda")


class SelfOrganisingMap:
    def __init__(self, shape, sigma=5., eta=5.):
        self.grid = torch.rand(*shape, device=device)
        self.sigma = sigma
        self.eta = eta

        self.row_idx, self.col_idx = torch.meshgrid([torch.arange(shape[0]), torch.arange(shape[1])])
        self.row_idx = self.row_idx.to(torch.float).to(device)
        self.col_idx = self.col_idx.to(torch.float).to(device)

    # returns the row / column indicies of the best matching unit for a given datapoint
    def get_BMU(self, x):
        idx = torch.argmin(torch.norm(self.grid - torch.tensor(x, device=device), dim=2))
        return idx / self.grid.shape[1], idx % self.grid.shape[1]

    def get_BMU_dist(self, x):
        return torch.norm(x-self.grid[self.get_BMU(x)])

    # returns an array representing the distance of each cell from the given row/col
    def dist(self, row, col):
        return torch.norm(torch.abs(torch.stack([self.row_idx - float(row), self.col_idx - float(col)], dim=2)), dim=2)

    def gauss(self, x, mu, sigma):
        return 1. / m.sqrt(2. * sigma * m.pi) * torch.exp(-torch.pow((x-mu),2) / (2.*sigma))

    def update(self, x):
        # get the best matching unit
        r,c = self.get_BMU(x)

        # now see how much we need to correct all the units around the BMU
        alpha = self.gauss(self.dist(r,c), 0, self.sigma).float()

        # now calculate how much to add to each of the neighbouring units
        delta = alpha.unsqueeze(2) * (x - self.grid)

        # lastly update the grid
        self.grid += (delta * self.eta)


if __name__ == '__main__':
    som = SelfOrganisingMap(shape=[100,100,3], sigma=50., eta=10.)

    x = [0.9, 0.95, 0.1]

    r,c = som.get_BMU(x)
    alpha = som.gauss(som.dist(r,c),0,som.sigma)
    delta = alpha.unsqueeze(2) * (torch.tensor(x, device=device) - som.grid)
    updated = som.grid + delta * som.eta

    # Show the update process
    for i, (title, img) in enumerate(zip(['original', 'dist', 'alpha', 'delta', 'updated'],[som.grid, som.dist(r,c), alpha, delta, updated])):
        plt.subplot(1, 5, i+1)
        plt.title(title)
        plt.imshow(img,interpolation='none')

    plt.show()

    # Show an updated map
    with TimeIt('mapping'):
        [som.update(torch.rand(1000,device=device)) for _ in range(10000)]
    
    plt.imshow(som.grid[:,:,:3])
    plt.show()
